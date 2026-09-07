from django.urls import path
from .views import SendOTPView, VerifyOTPView, UserProfileView, KYCSubmitView, SendEmailOTPView, VerifyEmailOTPView

urlpatterns = [
    path('auth/send-otp/', SendOTPView.as_view(), name='send_otp'),
    path('auth/verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('auth/send-email-otp/', SendEmailOTPView.as_view(), name='send_email_otp'),
    path('auth/verify-email-otp/', VerifyEmailOTPView.as_view(), name='verify_email_otp'),
    path('user/profile/', UserProfileView.as_view(), name='user_profile'),
    path('kyc/submit/', KYCSubmitView.as_view(), name='kyc_submit'),
]
