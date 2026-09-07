import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';
import '../utils/constants.dart';

class AuthProvider with ChangeNotifier {
  bool _isLoading = false;
  String? _token;
  final ApiService _apiService = ApiService();
  
  bool get isLoading => _isLoading;
  bool get isAuthenticated => _token != null;

  Future<bool> checkLoginStatus() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('access_token');
    notifyListeners();
    return _token != null;
  }

  Future<bool> sendOtp(String phone) async {
    _isLoading = true;
    notifyListeners();
    
    try {
      final response = await _apiService.post(
        ApiConstants.sendOtp, 
        {'phone': phone}
      );
      
      _isLoading = false;
      notifyListeners();
      
      if (response.statusCode == 200) {
        return true;
      }
      return false;
    } catch (e) {
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> verifyOtp(String phone, String otp) async {
    _isLoading = true;
    notifyListeners();
    
    try {
      final response = await _apiService.post(
        ApiConstants.verifyOtp, 
        {'phone': phone, 'otp': otp}
      );
      
      _isLoading = false;
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final prefs = await SharedPreferences.getInstance();
        _token = data['access'];
        await prefs.setString('access_token', _token!);
        await prefs.setString('refresh_token', data['refresh']);
        notifyListeners();
        return true;
      }
      notifyListeners();
      return false;
    } catch (e) {
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
    await prefs.remove('refresh_token');
    _token = null;
    notifyListeners();
  }
}
