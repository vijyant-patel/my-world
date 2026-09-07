import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/user_provider.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({Key? key}) : super(key: key);

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _salaryController = TextEditingController();
  final _companyController = TextEditingController();
  final _emailController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final user = Provider.of<UserProvider>(context, listen: false).user;
      if (user != null) {
        _nameController.text = user.name;
        _phoneController.text = user.phone;
        _salaryController.text = user.salary ?? '';
        _companyController.text = user.companyName ?? '';
        _emailController.text = user.email ?? '';
      }
    });
  }

  void _saveProfile() async {
    if (_formKey.currentState!.validate()) {
      final provider = Provider.of<UserProvider>(context, listen: false);
      final success = await provider.updateProfile({
        'name': _nameController.text,
        'salary': _salaryController.text,
        'company_name': _companyController.text,
        'email': _emailController.text,
      });

      if (mounted) {
        if (success) {
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Profile Updated Successfully')));
        } else {
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Failed to update profile')));
        }
      }
    }
  }

  void _verifyEmail() async {
    final email = _emailController.text;
    if (email.isEmpty) return;

    final provider = Provider.of<UserProvider>(context, listen: false);
    final success = await provider.sendEmailOtp(email);

    if (!mounted) return;

    if (success) {
      _showOtpDialog(email);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Failed to send OTP')));
    }
  }

  void _showOtpDialog(String email) {
    final otpController = TextEditingController();
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) {
        return AlertDialog(
          title: const Text('Verify Email OTP'),
          content: TextField(
            controller: otpController,
            keyboardType: TextInputType.number,
            decoration: const InputDecoration(hintText: 'Enter 6-digit OTP'),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () async {
                final provider = Provider.of<UserProvider>(context, listen: false);
                final verified = await provider.verifyEmailOtp(email, otpController.text);
                if (mounted) {
                  Navigator.pop(context);
                  if (verified) {
                    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Email Verified!')));
                  } else {
                    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Invalid OTP')));
                  }
                }
              },
              child: const Text('Verify'),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<UserProvider>(context);
    final user = provider.user;

    return Scaffold(
      appBar: AppBar(title: const Text('User Profile')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.orange.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.orange.shade300),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.warning_amber_rounded, color: Colors.orange),
                    SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Please ensure your salary details match your bank records to avoid rejection.',
                        style: TextStyle(color: Colors.deepOrange, fontWeight: FontWeight.w600),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(labelText: 'Full Name'),
                validator: (val) => val == null || val.isEmpty ? 'Required' : null,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _phoneController,
                decoration: const InputDecoration(labelText: 'Phone Number', filled: true, fillColor: Colors.black12),
                readOnly: true,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _companyController,
                decoration: const InputDecoration(labelText: 'Company Name'),
                validator: (val) => val == null || val.isEmpty ? 'Required' : null,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _salaryController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'Monthly Salary (₹)'),
                validator: (val) => val == null || val.isEmpty ? 'Required' : null,
              ),
              const SizedBox(height: 16),
              Row(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _emailController,
                      keyboardType: TextInputType.emailAddress,
                      decoration: const InputDecoration(labelText: 'Email Address'),
                      validator: (val) => val == null || val.isEmpty ? 'Required' : null,
                    ),
                  ),
                  if (user != null && !user.emailVerified) ...[
                    const SizedBox(width: 12),
                    ElevatedButton(
                      onPressed: provider.isLoading ? null : _verifyEmail,
                      style: ElevatedButton.styleFrom(backgroundColor: Colors.orange),
                      child: const Text('Verify', style: TextStyle(color: Colors.white)),
                    ),
                  ] else if (user != null && user.emailVerified) ...[
                    const SizedBox(width: 12),
                    const Icon(Icons.check_circle, color: Colors.green, size: 36),
                  ]
                ],
              ),
              const SizedBox(height: 32),
              ElevatedButton(
                onPressed: provider.isLoading ? null : _saveProfile,
                child: provider.isLoading 
                  ? const CircularProgressIndicator(color: Colors.white)
                  : const Text('Save Profile'),
              )
            ],
          ),
        ),
      ),
    );
  }
}
