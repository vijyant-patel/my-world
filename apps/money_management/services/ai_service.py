from abc import ABC, abstractmethod
from typing import List, Dict

class AIProvider(ABC):
    """
    Abstract interface for AI financial analysis providers.
    Ensures the module is not hardcoded to a specific vendor (OpenAI/Anthropic/Gemini).
    """
    @abstractmethod
    def analyze_financial_data(self, sanitized_data: dict) -> List[Dict]:
        """
        Receives purely numerical and non-PII financial data.
        Returns structured JSON recommendations matching the Phase 24 spec.
        """
        pass

class MockAIProvider(AIProvider):
    """
    Fallback/Mock provider if no real API key is configured.
    """
    def analyze_financial_data(self, sanitized_data: dict) -> List[Dict]:
        # Return a mock structured response
        return [{
            "title": "Accelerate Debt Payoff",
            "priority": "high",
            "category": "debt_payoff",
            "reason": "Based on your income-to-debt ratio, you have untapped payoff potential.",
            "current_state": "Paying minimum amounts.",
            "recommendation": "Allocate 20% of your surplus cash specifically towards your highest interest debt.",
            "estimated_impact": {
                "monthly_savings": 0,
                "interest_saved": 5000,
                "months_saved": 4
            },
            "confidence": "high",
            "requires_user_confirmation": True
        }]

class AIService:
    @staticmethod
    def get_provider() -> AIProvider:
        # In a real app, this would check django settings for which provider to load.
        # e.g., if settings.AI_PROVIDER == 'OPENAI': return OpenAIProvider()
        return MockAIProvider()

    @staticmethod
    def generate_recommendations(user) -> List[Dict]:
        """
        Gathers user's financial snapshot (without passwords/sensitive data)
        and asks the AI provider for recommendations.
        """
        from .cash_flow_service import CashFlowService
        from ..models import Debt
        import datetime
        
        now = datetime.datetime.now()
        flow = CashFlowService.get_monthly_cash_flow(user, now.year, now.month)
        net_worth = CashFlowService.get_net_worth(user)
        debts = list(Debt.objects.filter(user=user, is_closed=False).values('debt_type', 'outstanding_principal', 'interest_rate'))
        
        # Sanitize! No names, no contact infos, no account numbers.
        sanitized_data = {
            'monthly_income': float(flow['income']),
            'monthly_expenses': float(flow['expenses']),
            'monthly_debt_payments': float(flow['debt_payments']),
            'surplus': float(flow['surplus']),
            'net_worth': float(net_worth['net_worth']),
            'debts': [
                {
                    'type': d['debt_type'], 
                    'balance': float(d['outstanding_principal']), 
                    'rate': float(d['interest_rate'])
                } for d in debts
            ]
        }
        
        provider = AIService.get_provider()
        return provider.analyze_financial_data(sanitized_data)
