from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'money_management'

router = DefaultRouter()
router.register(r'accounts', views.MoneyAccountViewSet, basename='moneyaccount')
router.register(r'categories', views.MoneyCategoryViewSet, basename='moneycategory')
router.register(r'transactions', views.MoneyTransactionViewSet, basename='moneytransaction')
router.register(r'contacts', views.FinancialContactViewSet, basename='financialcontact')
router.register(r'debts', views.DebtViewSet, basename='debt')
router.register(r'debt-payments', views.DebtPaymentViewSet, basename='debtpayment')
router.register(r'goals', views.FinancialGoalViewSet, basename='financialgoal')
router.register(r'purchases', views.PlannedPurchaseViewSet, basename='plannedpurchase')
router.register(r'income-sources', views.IncomeSourceViewSet, basename='incomesource')

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    path('api/dashboard/summary/', views.DashboardAPIView.as_view({'get': 'summary'}), name='api_dashboard_summary'),
    path('api/strategies/compare/', views.StrategyAPIView.as_view({'get': 'compare'}), name='api_strategy_compare'),
    path('api/insights/recommendations/', views.InsightsAPIView.as_view({'get': 'recommendations'}), name='api_insights_recommendations'),
    
    # Frontend Template
    path('', views.MoneyDashboardView.as_view(), name='dashboard'),
]
