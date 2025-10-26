from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'kyc_status', 'is_active', 'date_joined')
    search_fields = ('email',)
    list_filter = ('kyc_status', 'is_active')
