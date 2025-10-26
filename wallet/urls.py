from django.urls import path
from . import views

urlpatterns = [
    # Wallet endpoints
    path('', views.WalletView.as_view(), name='wallet-detail'),
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    
    # Payment endpoints
    path('submit-payment/', views.submit_payment, name='submit-payment'),
    path('payment-requests/', views.get_payment_requests, name='payment-requests'),
    path('approve-payment/<int:payment_id>/', views.approve_payment, name='approve-payment'),
]
