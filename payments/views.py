from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer, CreatePaymentSerializer

class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).order_by('-created_at')

class CreatePaymentView(generics.CreateAPIView):
    serializer_class = CreatePaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # Generate mock gateway order ID for now
        import uuid
        gateway_order_id = f"order_{uuid.uuid4().hex[:8]}"
        
        serializer.save(
            user=self.request.user,
            gateway_order_id=gateway_order_id,
            status='INIT'
        )
