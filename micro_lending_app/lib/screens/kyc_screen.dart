import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../providers/user_provider.dart';

class KycScreen extends StatefulWidget {
  const KycScreen({Key? key}) : super(key: key);

  @override
  State<KycScreen> createState() => _KycScreenState();
}

class _KycScreenState extends State<KycScreen> {
  final _formKey = GlobalKey<FormState>();
  final _panController = TextEditingController();
  final _aadhaarController = TextEditingController();

  File? _panImage;
  File? _aadhaarImage;
  File? _selfieImage;

  final ImagePicker _picker = ImagePicker();

  Future<void> _pickImage(ImageSource source, String type) async {
    final XFile? image = await _picker.pickImage(source: source, imageQuality: 80);
    if (image != null) {
      setState(() {
        if (type == 'pan') _panImage = File(image.path);
        else if (type == 'aadhaar') _aadhaarImage = File(image.path);
        else if (type == 'selfie') _selfieImage = File(image.path);
      });
    }
  }

  void _submit() async {
    if (_formKey.currentState!.validate()) {
      if (_panImage == null || _aadhaarImage == null || _selfieImage == null) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please upload all required images.')));
        return;
      }

      final provider = Provider.of<UserProvider>(context, listen: false);
      final success = await provider.submitKyc(
        panNumber: _panController.text,
        aadhaarNumber: _aadhaarController.text,
        panPath: _panImage!.path,
        aadhaarPath: _aadhaarImage!.path,
        selfiePath: _selfieImage!.path,
      );

      if (success && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('KYC Submitted Successfully!')));
        Navigator.pop(context);
      } else if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('KYC Submission Failed')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final isLoading = Provider.of<UserProvider>(context).isLoading;

    return Scaffold(
      appBar: AppBar(title: const Text('Complete KYC')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextFormField(
                controller: _panController,
                decoration: const InputDecoration(labelText: 'PAN Number', border: OutlineInputBorder()),
                validator: (val) => val == null || val.isEmpty ? 'Required' : null,
              ),
              const SizedBox(height: 16),
              _buildImageSelector('Upload PAN Card', _panImage, 'pan'),
              
              const SizedBox(height: 24),
              TextFormField(
                controller: _aadhaarController,
                decoration: const InputDecoration(labelText: 'Aadhaar Number', border: OutlineInputBorder()),
                validator: (val) => val == null || val.isEmpty ? 'Required' : null,
              ),
              const SizedBox(height: 16),
              _buildImageSelector('Upload Aadhaar Card', _aadhaarImage, 'aadhaar'),
              
              const SizedBox(height: 24),
              _buildImageSelector('Take a Selfie', _selfieImage, 'selfie', isCamera: true),
              
              const SizedBox(height: 32),
              ElevatedButton(
                onPressed: isLoading ? null : _submit,
                child: isLoading 
                  ? const CircularProgressIndicator(color: Colors.white)
                  : const Text('Submit KYC'),
              )
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildImageSelector(String title, File? image, String type, {bool isCamera = false}) {
    return InkWell(
      onTap: () => _pickImage(isCamera ? ImageSource.camera : ImageSource.gallery, type),
      child: Container(
        height: 150,
        decoration: BoxDecoration(
          color: Colors.grey[200],
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.grey[400]!),
        ),
        child: image != null
          ? ClipRRect(borderRadius: BorderRadius.circular(12), child: Image.file(image, fit: BoxFit.cover))
          : Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(isCamera ? Icons.camera_alt : Icons.image, size: 40, color: Colors.grey[600]),
                const SizedBox(height: 8),
                Text(title, style: TextStyle(color: Colors.grey[600])),
              ],
            ),
      ),
    );
  }
}
