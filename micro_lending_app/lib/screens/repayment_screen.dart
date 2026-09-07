import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/loan_provider.dart';
import '../models/loan_model.dart';

class RepaymentScreen extends StatefulWidget {
  final LoanModel loan;
  const RepaymentScreen({Key? key, required this.loan}) : super(key: key);

  @override
  State<RepaymentScreen> createState() => _RepaymentScreenState();
}

class _RepaymentScreenState extends State<RepaymentScreen> {
  final _amountController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _amountController.text = widget.loan.totalPayable;
  }

  void _submit() async {
    final amount = _amountController.text;

    if (amount.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Enter valid amount')));
      return;
    }

    final provider = Provider.of<LoanProvider>(context, listen: false);
    final success = await provider.payRepayment(widget.loan.id, amount);

    if (!mounted) return;

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Payment Successful!')));
      Navigator.pop(context); // Go back
    } else {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Payment Failed.')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final isLoading = Provider.of<LoanProvider>(context).isLoading;

    return Scaffold(
      appBar: AppBar(title: const Text('Make Repayment')),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text('Loan #${widget.loan.id}', style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 16),
            Text('Total Payable: ₹${widget.loan.totalPayable}', style: const TextStyle(fontSize: 18)),
            const SizedBox(height: 32),
            TextField(
              controller: _amountController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Amount to Pay (₹)'),
            ),
            const SizedBox(height: 40),
            ElevatedButton(
              onPressed: isLoading ? null : _submit,
              child: isLoading 
                ? const CircularProgressIndicator(color: Colors.white)
                : const Text('Pay Now'),
            ),
          ],
        ),
      ),
    );
  }
}
