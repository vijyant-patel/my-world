from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import (MoneyAccount, MoneyCategory, MoneyTransaction, FinancialContact, Debt, 
                     DebtPayment, FinancialGoal, PlannedPurchase, IncomeSource)
from .serializers import (
    MoneyAccountSerializer, MoneyCategorySerializer, MoneyTransactionSerializer, 
    FinancialContactSerializer, DebtSerializer, DebtPaymentSerializer, 
    FinancialGoalSerializer, PlannedPurchaseSerializer, IncomeSourceSerializer
)
from .services.cash_flow_service import CashFlowService
from .services.affordability_service import AffordabilityService
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
import datetime
from decimal import Decimal

# User-isolated ViewSet Base
class UserIsolatedViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
        
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MoneyAccountViewSet(UserIsolatedViewSet):
    queryset = MoneyAccount.objects.all()
    serializer_class = MoneyAccountSerializer

class MoneyCategoryViewSet(UserIsolatedViewSet):
    queryset = MoneyCategory.objects.all()
    serializer_class = MoneyCategorySerializer

class MoneyTransactionViewSet(UserIsolatedViewSet):
    queryset = MoneyTransaction.objects.all().order_by('-date')
    serializer_class = MoneyTransactionSerializer

    def perform_create(self, serializer):
        # Automatically assign the first account if none provided
        account = serializer.validated_data.get('account')
        if not account:
            account = self.request.user.money_accounts.first()
        serializer.save(user=self.request.user, account=account)

class FinancialContactViewSet(UserIsolatedViewSet):
    queryset = FinancialContact.objects.all()
    serializer_class = FinancialContactSerializer

class IncomeSourceViewSet(UserIsolatedViewSet):
    queryset = IncomeSource.objects.all()
    serializer_class = IncomeSourceSerializer

class DebtViewSet(UserIsolatedViewSet):
    queryset = Debt.objects.all()
    serializer_class = DebtSerializer

class DebtPaymentViewSet(viewsets.ModelViewSet):
    queryset = DebtPayment.objects.all()
    serializer_class = DebtPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(debt__user=self.request.user)
        
    def perform_create(self, serializer):
        from decimal import Decimal
        from .services.interest_service import InterestService
        payment = serializer.save()
        debt = payment.debt
        
        # Simple allocation logic: Pay interest first, then principal.
        # Calculate pending interest (simplified for MVP: assume 30 days since last payment)
        pending_interest = InterestService.calculate_interest_for_debt(debt, days=30)
        
        if payment.amount >= pending_interest:
            payment.interest_allocated = pending_interest
            payment.principal_allocated = payment.amount - pending_interest
        else:
            payment.interest_allocated = payment.amount
            payment.principal_allocated = Decimal('0.00')
            
        payment.save()
        
        # Update Debt Outstanding
        debt.outstanding_principal -= payment.principal_allocated
        if debt.outstanding_principal <= 0:
            debt.is_closed = True
            debt.outstanding_principal = Decimal('0.00')
        debt.save()
        
        # Also create a unified MoneyTransaction for audibility
        from .models import MoneyTransaction
        # Find default account or create one
        account = self.request.user.money_accounts.first() 
        if account:
            MoneyTransaction.objects.create(
                user=self.request.user,
                account=account,
                debt_payment=payment,
                transaction_type='DEBT_PAYMENT',
                amount=payment.amount,
                date=payment.payment_date,
                description=f"Payment for {debt.name}"
            )

class FinancialGoalViewSet(UserIsolatedViewSet):
    queryset = FinancialGoal.objects.all()
    serializer_class = FinancialGoalSerializer

class PlannedPurchaseViewSet(UserIsolatedViewSet):
    queryset = PlannedPurchase.objects.all()
    serializer_class = PlannedPurchaseSerializer

    @action(detail=True, methods=['get'])
    def afford(self, request, pk=None):
        purchase = self.get_object()
        result = AffordabilityService.evaluate_purchase(request.user, purchase.price, purchase.target_date)
        return Response(result)

class DashboardAPIView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        now = datetime.datetime.now()
        
        # Ensure user has a default account
        if not MoneyAccount.objects.filter(user=request.user).exists():
            MoneyAccount.objects.create(user=request.user, name="Main Wallet", account_type="CASH")
            
        net_worth_data = CashFlowService.get_net_worth(request.user)
        cash_flow_data = CashFlowService.get_monthly_cash_flow(request.user, now.year, now.month)
        
        # Fetch Debts and Income sources for UI display
        active_debts = DebtSerializer(Debt.objects.filter(user=request.user, is_closed=False), many=True).data
        income_sources = IncomeSourceSerializer(IncomeSource.objects.filter(user=request.user, is_active=True), many=True).data
        
        return Response({
            'net_worth': net_worth_data,
            'cash_flow': cash_flow_data,
            'debts': active_debts,
            'income_sources': income_sources,
            'month': now.strftime("%B %Y")
        })

class StrategyAPIView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def compare(self, request):
        from .services.strategy_service import StrategyService
        debts = list(Debt.objects.filter(user=request.user, is_closed=False, debt_type='I_OWE'))
        
        # We calculate an estimated monthly surplus
        now = datetime.datetime.now()
        cash_flow = CashFlowService.get_monthly_cash_flow(request.user, now.year, now.month)
        surplus = cash_flow['surplus'] if cash_flow['surplus'] > 0 else Decimal('1000.00') # fallback
        
        snowball = StrategyService.project_payoff(debts, 'SNOWBALL', surplus)
        avalanche = StrategyService.project_payoff(debts, 'AVALANCHE', surplus)
        cash_flow_strategy = StrategyService.project_payoff(debts, 'CASH_FLOW', surplus)
        
        return Response({
            'snowball': snowball,
            'avalanche': avalanche,
            'cash_flow': cash_flow_strategy
        })

class InsightsAPIView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        from .services.rule_engine_service import RuleEngineService
        from .services.ai_service import AIService
        
        rule_insights = RuleEngineService.analyze_financials(request.user)
        ai_insights = AIService.generate_recommendations(request.user)
        
        return Response({
            'rules': rule_insights,
            'ai': ai_insights
        })

# Main Frontend Entry Point
class MoneyDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'money_management/dashboard.html'
