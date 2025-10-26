from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at')

class CreatePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('amount', 'gateway')
        
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value
