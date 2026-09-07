from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .serializers import UserSerializer, KYCSerializer, OTPSerializer, OTPVerifySerializer, EmailOTPSerializer, EmailOTPVerifySerializer
from .models import KYC
from .forms import CustomUserCreationForm

User = get_user_model()

class SendOTPView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            # For MVP: Hardcoded OTP simulation (in production, use SMS gateway)
            print(f"OTP for {phone} is 123456")
            return Response({"message": "OTP sent successfully (Simulated)"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            otp = serializer.validated_data['otp']
            
            # Simulated OTP validation
            if otp == "123456":
                user, created = User.objects.get_or_create(phone=phone)
                if created:
                    user.name = "New User" # To satisfy required field temporarily
                    user.save()
                    
                refresh = RefreshToken.for_user(user)
                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": UserSerializer(user).data
                })
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
        
    def put(self, request):
        user = request.user
        old_email = user.email
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            new_email = serializer.validated_data.get('email')
            if new_email and new_email != old_email:
                user.email_verified = False
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SendEmailOTPView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EmailOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = request.user
            if user.email != email:
                user.email = email
                user.email_verified = False
                user.save()
            # For MVP: Hardcoded OTP simulation (in production, use SMTP)
            print(f"OTP for {email} is 123456")
            return Response({"message": "Email OTP sent successfully (Simulated)"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailOTPView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EmailOTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            user = request.user
            
            if user.email != email:
                return Response({"error": "Email mismatch"}, status=status.HTTP_400_BAD_REQUEST)
                
            # Simulated OTP validation
            if otp == "123456":
                user.email_verified = True
                user.save()
                return Response({"message": "Email verified successfully", "user": UserSerializer(user).data})
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class KYCSubmitView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        kyc, created = KYC.objects.get_or_create(user=user)
        serializer = KYCSerializer(kyc, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            user.kyc_status = 'VERIFIED' # Auto verify for MVP
            user.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('interviews:dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
