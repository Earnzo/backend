from django.contrib import admin
from .models import Stake

@admin.register(Stake)
class StakeAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'daily_payout', 'state', 'created_at')
    list_filter = ('state',)
