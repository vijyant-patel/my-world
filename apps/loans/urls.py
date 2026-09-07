from django.urls import path
from .views import ApplyLoanView, LoanStatusView, RiskScoreView

urlpatterns = [
    path('apply/', ApplyLoanView.as_view(), name='apply_loan'),
    path('status/', LoanStatusView.as_view(), name='loan_status'),
    path('risk-score/', RiskScoreView.as_view(), name='risk_score'),
]
