from rest_framework import serializers
from .models import Repayment

class RepaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repayment
        fields = ['id', 'loan', 'amount_paid', 'date', 'status', 'transaction_id', 'late_penalty']
        read_only_fields = ['id', 'date', 'status', 'transaction_id', 'late_penalty']
