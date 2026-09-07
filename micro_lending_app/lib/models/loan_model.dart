class LoanModel {
  final int id;
  final String amount;
  final int tenure;
  final String interestRate;
  final String status;
  final String? dueDate;
  final String totalPayable;
  final String createdAt;

  LoanModel({
    required this.id,
    required this.amount,
    required this.tenure,
    required this.interestRate,
    required this.status,
    this.dueDate,
    required this.totalPayable,
    required this.createdAt,
  });

  factory LoanModel.fromJson(Map<String, dynamic> json) {
    return LoanModel(
      id: json['id'],
      amount: json['amount'].toString(),
      tenure: json['tenure'],
      interestRate: json['interest_rate'].toString(),
      status: json['status'],
      dueDate: json['due_date'],
      totalPayable: json['total_payable'].toString(),
      createdAt: json['created_at'],
    );
  }
}
