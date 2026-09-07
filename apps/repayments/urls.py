from django.urls import path
from .views import PayRepaymentView

urlpatterns = [
    path('pay/', PayRepaymentView.as_view(), name='pay_repayment'),
]
