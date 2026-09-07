from decimal import Decimal
from typing import List
from ..models import Debt

class StrategyService:
    @staticmethod
    def get_debts_ordered_by_strategy(debts: List[Debt], strategy: str) -> List[Debt]:
        """
        Orders a list of active debts based on the chosen payoff strategy.
        """
        if strategy == 'SNOWBALL':
            # Lowest balance first
            return sorted(debts, key=lambda d: d.outstanding_principal)
        
        elif strategy == 'AVALANCHE':
            # Highest interest rate first
            # We assume EMI and SIMPLE_YEARLY share the same rate scale.
            # If interest_type is NONE, rate is effectively 0.
            def effective_rate(d):
                if d.interest_type == 'NONE': return Decimal('-1.0')
                return d.interest_rate
            return sorted(debts, key=lambda d: effective_rate(d), reverse=True)
        
        elif strategy == 'CASH_FLOW':
            # Prioritize freeing up the highest monthly payment relative to the balance
            # Ratio = Monthly Payment / Outstanding Balance (Highest ratio = quickest cash flow relief)
            def cash_flow_ratio(d):
                if d.outstanding_principal <= 0: return Decimal('0')
                return d.expected_monthly_payment / d.outstanding_principal
            return sorted(debts, key=lambda d: cash_flow_ratio(d), reverse=True)
        
        # Default fallback
        return debts

    @staticmethod
    def project_payoff(debts: List[Debt], strategy: str, available_monthly_surplus: Decimal):
        """
        Simulates the payoff journey given a strategy and extra monthly cash.
        Returns a projected timeline (Not fully implemented yet for MVP phase).
        """
        ordered_debts = StrategyService.get_debts_ordered_by_strategy(debts, strategy)
        target_name = ordered_debts[0].name if ordered_debts else "None"
        
        return {
            'strategy': strategy,
            'target_name': target_name,
            'ordered_debt_ids': [d.id for d in ordered_debts],
            'estimated_months': len(ordered_debts) * 12 # Placeholder math
        }
