from rest_framework import serializers
from .models import Stake

class StakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stake
        fields = '__all__'
        read_only_fields = ('id', 'user', 'state', 'created_at', 'next_payout_date', 'payouts_remaining')

class CreateStakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stake
        fields = ('amount', 'duration_days')
    
    def validate_amount(self, value):
        if value < 500:
            raise serializers.ValidationError("Minimum stake amount is ₹500")
        return value
