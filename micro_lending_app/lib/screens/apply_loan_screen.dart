import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/loan_provider.dart';

class ApplyLoanScreen extends StatefulWidget {
  const ApplyLoanScreen({Key? key}) : super(key: key);

  @override
  State<ApplyLoanScreen> createState() => _ApplyLoanScreenState();
}

class _ApplyLoanScreenState extends State<ApplyLoanScreen> {
  final _amountController = TextEditingController();
  final _tenureController = TextEditingController();

  void _submit() async {
    final amount = _amountController.text;
    final tenure = int.tryParse(_tenureController.text) ?? 0;

    if (amount.isEmpty || tenure <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Enter valid amount and tenure')));
      return;
    }

    final provider = Provider.of<LoanProvider>(context, listen: false);
    final success = await provider.applyLoan(amount, tenure);

    if (!mounted) return;

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Loan applied successfully!')));
      Navigator.pop(context);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Loan application rejected or failed.')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final isLoading = Provider.of<LoanProvider>(context).isLoading;

    return Scaffold(
      appBar: AppBar(title: const Text('Apply for Loan')),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: _amountController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Loan Amount (₹)'),
            ),
            const SizedBox(height: 20),
            TextField(
              controller: _tenureController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Tenure (Months)'),
            ),
            const SizedBox(height: 40),
            ElevatedButton(
              onPressed: isLoading ? null : _submit,
              child: isLoading 
                ? const CircularProgressIndicator(color: Colors.white)
                : const Text('Submit Application'),
            ),
          ],
        ),
      ),
    );
  }
}
