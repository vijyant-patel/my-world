import 'dart:convert';
import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../utils/constants.dart';
import '../models/loan_model.dart';

class LoanProvider with ChangeNotifier {
  bool _isLoading = false;
  List<LoanModel> _loans = [];
  final ApiService _apiService = ApiService();

  bool get isLoading => _isLoading;
  List<LoanModel> get loans => _loans;

  Future<void> fetchLoans() async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await _apiService.get(ApiConstants.loanStatus);
      if (response.statusCode == 200) {
        List<dynamic> data = jsonDecode(response.body);
        _loans = data.map((json) => LoanModel.fromJson(json)).toList();
      }
    } catch (e) {
      debugPrint('Error fetching loans: $e');
    }

    _isLoading = false;
    notifyListeners();
  }

  Future<bool> applyLoan(String amount, int tenure) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await _apiService.post(
        ApiConstants.applyLoan,
        {
          'amount': amount,
          'tenure': tenure,
        }
      );

      _isLoading = false;
      notifyListeners();

      if (response.statusCode == 201) {
        await fetchLoans();
        return true;
      }
      return false;
    } catch (e) {
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> payRepayment(int loanId, String amountPaid) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await _apiService.post(
        ApiConstants.payRepayment,
        {
          'loan': loanId,
          'amount_paid': amountPaid,
        }
      );

      _isLoading = false;
      notifyListeners();

      if (response.statusCode == 201) {
        await fetchLoans(); // Refresh loan list
        return true;
      }
      return false;
    } catch (e) {
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }
}
