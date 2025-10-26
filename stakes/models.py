from django.db import models
from django.conf import settings
import uuid

class Stake(models.Model):
    STATE_CHOICES = [
        ('PENDING_PAYMENT', 'Pending Payment'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    daily_payout = models.DecimalField(max_digits=14, decimal_places=2)
    duration_days = models.IntegerField(default=60)
    start_date = models.DateField(null=True, blank=True)
    next_payout_date = models.DateField(null=True, blank=True)
    payouts_remaining = models.IntegerField(null=True, blank=True)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='PENDING_PAYMENT')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Stake {self.id} - {self.user.email}"
