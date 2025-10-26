from django.db import models
from django.conf import settings
import uuid

class Payment(models.Model):
    STATUS_CHOICES = [
        ('INIT', 'Initialized'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stake = models.ForeignKey('stakes.Stake', on_delete=models.SET_NULL, null=True, blank=True)
    gateway = models.CharField(max_length=30)
    gateway_order_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    raw_gateway_payload = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.gateway_order_id} - {self.status}"
