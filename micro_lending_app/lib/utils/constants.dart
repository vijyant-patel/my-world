class ApiConstants {
  // Use 10.0.2.2 for Android emulator to access localhost, or 127.0.0.1 for iOS simulator.
  // For physical devices, use your computer's local IP address (e.g., 192.168.x.x)
  static const String baseUrl = 'http://localhost:8000/api';
  
  static const String sendOtp = '$baseUrl/users/auth/send-otp/';
  static const String verifyOtp = '$baseUrl/users/auth/verify-otp/';
  static const String sendEmailOtp = '$baseUrl/users/auth/send-email-otp/';
  static const String verifyEmailOtp = '$baseUrl/users/auth/verify-email-otp/';
  static const String profile = '$baseUrl/users/user/profile/';
  static const String kycSubmit = '$baseUrl/users/kyc/submit/';
  
  static const String applyLoan = '$baseUrl/loans/apply/';
  static const String loanStatus = '$baseUrl/loans/status/';
  
  static const String payRepayment = '$baseUrl/repayments/pay/';
}
