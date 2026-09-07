import 'dart:convert';
import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../utils/constants.dart';
import '../models/user_model.dart';

class UserProvider with ChangeNotifier {
  bool _isLoading = false;
  UserModel? _user;
  final ApiService _apiService = ApiService();

  bool get isLoading => _isLoading;
  UserModel? get user => _user;

  Future<void> fetchProfile() async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await _apiService.get(ApiConstants.profile);
      if (response.statusCode == 200) {
        _user = UserModel.fromJson(jsonDecode(response.body));
      }
    } catch (e) {
      debugPrint('Error fetching profile: $e');
    }

    _isLoading = false;
    notifyListeners();
  }

  Future<bool> submitKyc({
    required String panNumber,
    required String aadhaarNumber,
    required String panPath,
    required String aadhaarPath,
    required String selfiePath,
  }) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await _apiService.multipartRequest(
        ApiConstants.kycSubmit,
        {
          'pan_number': panNumber,
          'aadhaar_number': aadhaarNumber,
        },
        {
          'pan_card': panPath,
          'aadhaar_card': aadhaarPath,
          'selfie': selfiePath,
        }
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        await fetchProfile(); // refresh user profile
        return true;
      }
    } catch (e) {
      debugPrint('KYC Submit Error: $e');
    }

    _isLoading = false;
    notifyListeners();
    return false;
  }

  Future<bool> updateProfile(Map<String, dynamic> data) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await _apiService.put(ApiConstants.profile, data);
      if (response.statusCode == 200) {
        _user = UserModel.fromJson(jsonDecode(response.body));
        _isLoading = false;
        notifyListeners();
        return true;
      }
    } catch (e) {
      debugPrint('Profile update error: $e');
    }

    _isLoading = false;
    notifyListeners();
    return false;
  }

  Future<bool> sendEmailOtp(String email) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await _apiService.post(ApiConstants.sendEmailOtp, {'email': email});
      _isLoading = false;
      notifyListeners();
      return response.statusCode == 200;
    } catch (e) {
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> verifyEmailOtp(String email, String otp) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await _apiService.post(ApiConstants.verifyEmailOtp, {'email': email, 'otp': otp});
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _user = UserModel.fromJson(data['user']);
        _isLoading = false;
        notifyListeners();
        return true;
      }
    } catch (e) {
      debugPrint('Email OTP Verify Error: $e');
    }

    _isLoading = false;
    notifyListeners();
    return false;
  }
}
