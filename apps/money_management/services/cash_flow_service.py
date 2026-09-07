from decimal import Decimal
from django.db.models import Sum
from ..models import MoneyAccount, Debt, MoneyTransaction

class CashFlowService:
    @staticmethod
    def get_net_worth(user) -> dict:
        """
        Net Worth = Total Assets - Total Liabilities
        Assets = Sum of Bank, Cash, Savings, Investment balances
        Liabilities = Sum of Credit Cards + Outstanding Debts
        """
        accounts = MoneyAccount.objects.filter(user=user, is_active=True)
        
        # Simple separation: Credit Cards are liabilities, others are assets.
        assets = accounts.exclude(account_type='CREDIT_CARD').aggregate(total=Sum('balance'))['total'] or Decimal('0.00')
        cc_liabilities = accounts.filter(account_type='CREDIT_CARD').aggregate(total=Sum('balance'))['total'] or Decimal('0.00')
        
        # I_OWE debts are liabilities
        debts = Debt.objects.filter(user=user, is_closed=False, debt_type='I_OWE').aggregate(total=Sum('outstanding_principal'))['total'] or Decimal('0.00')
        
        # OWED_TO_ME debts are assets
        owed_to_me = Debt.objects.filter(user=user, is_closed=False, debt_type='OWED_TO_ME').aggregate(total=Sum('outstanding_principal'))['total'] or Decimal('0.00')
        
        total_assets = assets + owed_to_me
        total_liabilities = cc_liabilities + debts
        
        return {
            'assets': total_assets,
            'liabilities': total_liabilities,
            'net_worth': total_assets - total_liabilities
        }

    @staticmethod
    def get_monthly_cash_flow(user, year: int, month: int) -> dict:
        """
        Calculates income vs expenses for a specific month.
        """
        transactions = MoneyTransaction.objects.filter(
            user=user, 
            date__year=year, 
            date__month=month
        )
        
        income = transactions.filter(transaction_type='INCOME').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        expenses = transactions.filter(transaction_type='EXPENSE').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        debt_payments = transactions.filter(transaction_type='DEBT_PAYMENT').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        return {
            'income': income,
            'expenses': expenses,
            'debt_payments': debt_payments,
            'surplus': income - expenses - debt_payments
        }
