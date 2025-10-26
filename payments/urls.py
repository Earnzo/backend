from django.urls import path
from .views import PaymentListView, CreatePaymentView

urlpatterns = [
    path('', PaymentListView.as_view(), name='payment_list'),
    path('create/', CreatePaymentView.as_view(), name='payment_create'),
]
