from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import KYC

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'name', 'salary', 'kyc_status', 'email', 'company_name', 'email_verified']
        read_only_fields = ['id', 'kyc_status', 'email_verified']

class KYCSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYC
        fields = ['pan_card', 'aadhaar_card', 'selfie', 'pan_number', 'aadhaar_number', 'submitted_at']

class OTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)

class OTPVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)

class EmailOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

class EmailOTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
