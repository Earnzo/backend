from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('users.urls')),
    path('api/v1/wallet/', include('wallet.urls')),
    path('api/v1/stakes/', include('stakes.urls')),
    path('api/v1/payments/', include('payments.urls')),
]
