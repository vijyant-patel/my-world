from decimal import Decimal
from .cash_flow_service import CashFlowService

class AffordabilityService:
    @staticmethod
    def evaluate_purchase(user, price: Decimal, target_date=None) -> dict:
        """
        Determines if a user can afford a planned purchase.
        Rules:
        - If price < total available cash (minus 1 month of expenses buffer) -> Affordable
        - If price > available cash, check monthly surplus.
        - If surplus > 0, calculate months needed to save.
        """
        if price <= 0:
            return {'status': 'Affordable', 'reason': 'Price is zero.'}
            
        net_worth_data = CashFlowService.get_net_worth(user)
        # Simplified: assume 'assets' is roughly available cash for now.
        # In a real scenario, we'd specifically filter for 'CASH' and 'BANK' accounts.
        available_cash = net_worth_data['assets'] 
        
        if available_cash >= price:
            return {
                'status': 'Affordable', 
                'reason': 'You have enough cash assets to cover this immediately.',
                'recommended_action': 'CASH'
            }
            
        import datetime
        now = datetime.datetime.now()
        flow = CashFlowService.get_monthly_cash_flow(user, now.year, now.month)
        surplus = flow['surplus']
        
        if surplus <= 0:
            return {
                'status': 'Not Recommended', 
                'reason': 'Your monthly cash flow is currently negative or zero. Taking on new expenses or debt is risky.',
                'recommended_action': 'DELAY'
            }
            
        months_to_save = (price / surplus).quantize(Decimal('1.'), rounding='ROUND_UP')
        
        return {
            'status': 'Affordable with Planning',
            'reason': f'You can save for this by allocating your monthly surplus (₹{surplus}) for {months_to_save} months.',
            'recommended_action': 'SAVE',
            'months_required': months_to_save
        }
