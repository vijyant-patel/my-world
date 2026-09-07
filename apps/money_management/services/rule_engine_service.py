from decimal import Decimal
from typing import List
from ..models import Debt, MoneyAccount
from .cash_flow_service import CashFlowService

class RuleEngineService:
    @staticmethod
    def analyze_financials(user) -> List[dict]:
        """
        Runs deterministic non-AI rules to generate financial insights.
        """
        insights = []
        
        # Rule 1: High Interest Debt Alert
        high_interest_threshold = Decimal('15.00') # 15% annual
        high_interest_debts = Debt.objects.filter(
            user=user, 
            is_closed=False, 
            debt_type='I_OWE', 
            interest_rate__gte=high_interest_threshold,
            interest_type__in=['SIMPLE_YEARLY', 'EMI']
        )
        for debt in high_interest_debts:
            insights.append({
                'rule_name': 'High Interest Debt Alert',
                'severity': 'HIGH',
                'title': f'High Interest on {debt.name}',
                'explanation': f'This debt carries an interest rate of {debt.interest_rate}%, which is very high.',
                'suggested_action': 'Prioritize paying this off using the Avalanche strategy to minimize interest lost.'
            })
            
        # Rule 2: Emergency Buffer Check
        # Check if cash accounts cover at least 3 months of expenses
        import datetime
        now = datetime.datetime.now()
        flow = CashFlowService.get_monthly_cash_flow(user, now.year, now.month)
        expenses = flow['expenses']
        
        if expenses > 0:
            accounts = MoneyAccount.objects.filter(user=user, is_active=True, account_type__in=['CASH', 'BANK', 'SAVINGS'])
            total_cash = sum(acc.balance for acc in accounts)
            recommended_buffer = expenses * Decimal('3')
            
            if total_cash < recommended_buffer:
                shortfall = recommended_buffer - total_cash
                insights.append({
                    'rule_name': 'Emergency Buffer Warning',
                    'severity': 'MEDIUM',
                    'title': 'Low Cash Buffer',
                    'explanation': f'Your liquid cash is ₹{total_cash}, but we recommend a 3-month expense buffer of ₹{recommended_buffer}.',
                    'suggested_action': f'Save an additional ₹{shortfall} in your savings account before making aggressive extra debt payments.'
                })
                
        # Rule 3: Negative Cash Flow Warning
        if flow['surplus'] < 0:
            insights.append({
                'rule_name': 'Negative Cash Flow',
                'severity': 'CRITICAL',
                'title': 'You are spending more than you earn',
                'explanation': f'This month, your expenses and debt payments exceed your income by ₹{abs(flow["surplus"])}.',
                'suggested_action': 'Review your expenses immediately and find areas to cut back to avoid accumulating more debt.'
            })
            
        return insights
