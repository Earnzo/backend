from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import logging

from .models import Wallet, Transaction, PaymentRequest
from .serializers import WalletSerializer, TransactionSerializer, PaymentRequestSerializer

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_payment(request):
    """User submits payment with transaction ID"""
    
    # Log incoming request
    logger.info(f"Payment submission from user: {request.user.email}")
    logger.info(f"Request data: {request.data}")
    
    # Extract data
    amount = request.data.get('amount')
    transaction_id = request.data.get('transaction_id')
    upi_ref_id = request.data.get('upi_ref_id', '')
    notes = request.data.get('notes', '')
    
    # Validate required fields
    if not amount or not transaction_id:
        logger.error("Missing required fields: amount or transaction_id")
        return Response(
            {'error': 'Amount and transaction ID are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Wrap in atomic transaction
        with transaction.atomic():
            # Convert amount to Decimal
            amount_decimal = Decimal(str(amount))
            
            if amount_decimal <= 0:
                return Response(
                    {'error': 'Amount must be greater than 0'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check for duplicate transaction ID
            if PaymentRequest.objects.filter(transaction_id=transaction_id).exists():
                logger.error(f"Duplicate transaction ID: {transaction_id}")
                return Response(
                    {'error': 'Transaction ID already submitted'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create payment request
            logger.info(f"Creating PaymentRequest for {request.user.email}")
            payment_request = PaymentRequest.objects.create(
                user=request.user,
                amount=amount_decimal,
                transaction_id=transaction_id,
                upi_ref_id=upi_ref_id,
                status='PENDING',
                notes=notes
            )
            
            logger.info(f"PaymentRequest created with ID: {payment_request.id}")
            
            # Update wallet pending balance
            logger.info(f"Updating wallet for user: {request.user.email}")
            wallet, created = Wallet.objects.get_or_create(
                user=request.user,
                defaults={'balance': 0, 'pending_balance': 0}
            )
            wallet.pending_balance += amount_decimal
            wallet.save()
            
            logger.info(f"Wallet updated. New pending balance: {wallet.pending_balance}")
        
        return Response({
            'success': True,
            'message': f'Payment of ₹{amount} submitted for verification',
            'payment_id': payment_request.id,
            'status': 'PENDING'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error in submit_payment: {str(e)}")
        return Response(
            {'error': f'Payment submission failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_payment_requests(request):
    """Get user's payment requests"""
    payments = PaymentRequest.objects.filter(user=request.user).order_by('-created_at')
    serializer = PaymentRequestSerializer(payments, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def approve_payment(request, payment_id):
    """Admin approve payment request"""
    try:
        with transaction.atomic():
            payment_request = PaymentRequest.objects.get(id=payment_id)
            
            if payment_request.status != 'PENDING':
                return Response(
                    {'error': 'Payment already processed'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update payment request
            payment_request.status = 'APPROVED'
            payment_request.approved_at = timezone.now()
            payment_request.approved_by = request.user
            payment_request.save()
            
            # Update user wallet
            wallet, created = Wallet.objects.get_or_create(user=payment_request.user)
            wallet.balance += payment_request.amount
            if wallet.pending_balance >= payment_request.amount:
                wallet.pending_balance -= payment_request.amount
            else:
                wallet.pending_balance = 0
            wallet.save()
            
            # Create transaction record
            Transaction.objects.create(
                user=payment_request.user,
                type='TOPUP',
                amount=payment_request.amount,
                balance_after=wallet.balance,
                payment_request=payment_request,
                metadata={'approved_by': request.user.email}
            )
        
        return Response({
            'success': True,
            'message': f'Payment approved for {payment_request.user.email}'
        })
        
    except PaymentRequest.DoesNotExist:
        return Response(
            {'error': 'Payment request not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

class WalletView(generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        wallet, created = Wallet.objects.get_or_create(
            user=self.request.user,
            defaults={'balance': 0, 'pending_balance': 0}
        )
        return wallet

class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-created_at')
