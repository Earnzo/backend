from rest_framework import serializers
from .models import PaymentRequest, Wallet, Transaction

class PaymentRequestSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = PaymentRequest
        fields = [
            'id', 'user_email', 'amount', 'transaction_id', 
            'upi_ref_id', 'status', 'created_at', 'approved_at', 'notes'
        ]
        read_only_fields = ['id', 'user_email', 'status', 'created_at', 'approved_at']

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['balance', 'pending_balance', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id', 'type', 'amount', 'balance_after', 
            'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
