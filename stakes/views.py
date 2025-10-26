from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Stake
from .serializers import StakeSerializer, CreateStakeSerializer

class StakeCreateView(generics.CreateAPIView):
    serializer_class = CreateStakeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Calculate daily payout based on amount
        amount = serializer.validated_data['amount']
        daily_payout = self.calculate_daily_payout(amount)
        
        serializer.save(
            user=self.request.user,
            daily_payout=daily_payout,
            state='PENDING_PAYMENT'
        )


    def calculate_daily_payout(self, amount):
        # Payout tiers as per SRS
        if 500 <= amount <= 699:
            return 30
        elif 700 <= amount <= 999:
            return 45
        elif 1000 <= amount <= 1999:
            return 70
        else:
            # For amounts above 1999, use a formula
            return round(amount * 0.065)  # 6.5% daily return

class StakeListView(generics.ListAPIView):
    serializer_class = StakeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Stake.objects.filter(user=self.request.user).order_by('-created_at')

class StakeDetailView(generics.RetrieveAPIView):
    serializer_class = StakeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Stake.objects.filter(user=self.request.user)
