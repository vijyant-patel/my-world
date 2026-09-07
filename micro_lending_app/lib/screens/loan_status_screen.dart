import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/loan_provider.dart';
import 'repayment_screen.dart';

class LoanStatusScreen extends StatefulWidget {
  const LoanStatusScreen({Key? key}) : super(key: key);

  @override
  State<LoanStatusScreen> createState() => _LoanStatusScreenState();
}

class _LoanStatusScreenState extends State<LoanStatusScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<LoanProvider>(context, listen: false).fetchLoans();
    });
  }

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<LoanProvider>(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Loan History')),
      body: provider.isLoading
        ? const Center(child: CircularProgressIndicator())
        : provider.loans.isEmpty
          ? const Center(child: Text('No loans found.'))
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: provider.loans.length,
              itemBuilder: (context, index) {
                final loan = provider.loans[index];
                return Card(
                  margin: const EdgeInsets.only(bottom: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  child: ListTile(
                    contentPadding: const EdgeInsets.all(16),
                    title: Text('Loan #${loan.id} - ₹${loan.amount}', style: const TextStyle(fontWeight: FontWeight.bold)),
                    subtitle: Text('Status: ${loan.status}\nTenure: ${loan.tenure} months'),
                    trailing: loan.status == 'ACTIVE' || loan.status == 'DEFAULTED' ? ElevatedButton(
                      onPressed: () {
                        Navigator.push(context, MaterialPageRoute(builder: (_) => RepaymentScreen(loan: loan)));
                      },
                      child: const Text('Pay'),
                    ) : Text('Payable:\n₹${loan.totalPayable}', textAlign: TextAlign.right, style: TextStyle(color: Theme.of(context).primaryColor, fontWeight: FontWeight.bold)),
                  ),
                );
              },
            ),
    );
  }
}
