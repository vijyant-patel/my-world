from rest_framework import serializers
from .models import Loan, RiskScore

class LoanSerializer(serializers.ModelSerializer):
    total_payable = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = Loan
        fields = ['id', 'amount', 'tenure', 'interest_rate', 'status', 'due_date', 'total_payable', 'created_at']
        read_only_fields = ['id', 'status', 'due_date', 'interest_rate', 'total_payable', 'created_at']

class RiskScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskScore
        fields = ['score', 'decision', 'evaluated_at']
