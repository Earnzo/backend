from django.contrib import admin
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import PaymentRequest, Wallet, Transaction

@admin.register(PaymentRequest)
class PaymentRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'transaction_id', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'transaction_id')
    readonly_fields = ('created_at', 'approved_at')
    actions = ['approve_payments', 'reject_payments']
    
    def approve_payments(self, request, queryset):
        """Approve selected pending payments and send real-time updates"""
        channel_layer = get_channel_layer()
        approved_count = 0
        
        for payment in queryset.filter(status='PENDING'):
            # Update payment status
            payment.status = 'APPROVED'
            payment.approved_at = timezone.now()
            payment.approved_by = request.user
            payment.save()
            
            # Update or create wallet
            wallet, created = Wallet.objects.get_or_create(user=payment.user)
            wallet.balance += payment.amount
            
            if wallet.pending_balance >= payment.amount:
                wallet.pending_balance -= payment.amount
            else:
                wallet.pending_balance = 0
            wallet.save()
            
            # Create transaction record
            Transaction.objects.create(
                user=payment.user,
                type='TOPUP',
                amount=payment.amount,
                balance_after=wallet.balance,
                payment_request=payment,
                metadata={
                    'approved_by': request.user.email,
                    'transaction_id': payment.transaction_id,
                    'approval_date': timezone.now().isoformat()
                }
            )
            
            # Send real-time update to user's WebSocket (if available)
            if channel_layer:
                wallet_group_name = f'wallet_{payment.user.id}'
                async_to_sync(channel_layer.group_send)(
                    wallet_group_name,
                    {
                        'type': 'wallet_update',
                        'balance': wallet.balance,
                        'pending_balance': wallet.pending_balance,
                        'message': f'Payment of ₹{payment.amount} has been approved!'
                    }
                )
            
            approved_count += 1
        
        if approved_count > 0:
            self.message_user(
                request, 
                f"✅ {approved_count} payment(s) approved successfully!"
            )
    
    approve_payments.short_description = "✅ Approve selected payments"
    
    def reject_payments(self, request, queryset):
        """Reject selected pending payments"""
        rejected_count = queryset.filter(status='PENDING').update(
            status='REJECTED',
            approved_at=timezone.now(),
            approved_by=request.user
        )
        
        if rejected_count > 0:
            self.message_user(request, f"❌ {rejected_count} payment(s) rejected.")
    
    reject_payments.short_description = "❌ Reject selected payments"

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'pending_balance', 'created_at')
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'amount', 'balance_after', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('user__email',)
    readonly_fields = ('created_at',)
