class UserModel {
  final int id;
  final String phone;
  final String name;
  final String? email;
  final String? salary;
  final String? companyName;
  final String kycStatus;
  final bool emailVerified;

  UserModel({
    required this.id,
    required this.phone,
    required this.name,
    this.email,
    this.salary,
    this.companyName,
    required this.kycStatus,
    this.emailVerified = false,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'],
      phone: json['phone'] ?? '',
      name: json['name'] ?? '',
      email: json['email'],
      salary: json['salary']?.toString(),
      companyName: json['company_name'],
      kycStatus: json['kyc_status'] ?? 'PENDING',
      emailVerified: json['email_verified'] ?? false,
    );
  }
}
