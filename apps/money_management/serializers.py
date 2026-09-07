from rest_framework import serializers
from .models import MoneyAccount, MoneyCategory, MoneyTransaction, FinancialContact, Debt, DebtPayment, FinancialGoal, PlannedPurchase, IncomeSource

class MoneyAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoneyAccount
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']

class MoneyCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MoneyCategory
        fields = '__all__'
        read_only_fields = ['user']

class MoneyTransactionSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = MoneyTransaction
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

class FinancialContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialContact
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

class DebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debt
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']

class DebtPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DebtPayment
        fields = '__all__'
        read_only_fields = ['created_at']

class FinancialGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialGoal
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

class PlannedPurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlannedPurchase
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

class IncomeSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeSource
        fields = '__all__'
        read_only_fields = ['user', 'created_at']
