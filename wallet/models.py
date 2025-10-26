from django.db import models
from django.conf import settings
from decimal import Decimal

class PaymentRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True)
    upi_ref_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name='approved_payments'
    )
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.email} - ₹{self.amount} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    pending_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Wallet: {self.user.email} - ₹{self.balance}"

class Transaction(models.Model):
    TYPE_CHOICES = [
        ('TOPUP', 'Top Up'),
        ('PAYOUT', 'Payout'),
        ('STAKE_CREATION', 'Stake Creation'),
        ('WITHDRAWAL', 'Withdrawal'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    balance_after = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    payment_request = models.ForeignKey(
        PaymentRequest, 
        on_delete=models.CASCADE, 
        null=True, blank=True
    )
    metadata = models.JSONField(blank=True, null=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.type} - ₹{self.amount}"
    
    class Meta:
        ordering = ['-created_at']
