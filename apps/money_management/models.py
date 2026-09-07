from django.db import models
from django.conf import settings
from decimal import Decimal
from django.core.validators import MinValueValidator

class MoneyAccount(models.Model):
    ACCOUNT_TYPES = [
        ('CASH', 'Cash'),
        ('BANK', 'Bank Account'),
        ('SAVINGS', 'Savings Account'),
        ('WALLET', 'Digital Wallet'),
        ('CREDIT_CARD', 'Credit Card'),
        ('INVESTMENT', 'Investment Account'),
        ('LOAN', 'Loan Account'),
        ('OTHER', 'Other')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='money_accounts')
    name = models.CharField(max_length=255)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='BANK')
    institution = models.CharField(max_length=255, blank=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=10, default='INR')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"

class MoneyCategory(models.Model):
    CATEGORY_TYPES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='money_categories')
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name_plural = 'Money categories'
        unique_together = ('user', 'name', 'category_type')

    def __str__(self):
        return f"{self.name} ({self.category_type})"

class FinancialContact(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='financial_contacts')
    name = models.CharField(max_length=255)
    relationship = models.CharField(max_length=100, blank=True)
    contact_info = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Debt(models.Model):
    DEBT_TYPES = [
        ('I_OWE', 'I owe someone (Borrowing)'),
        ('OWED_TO_ME', 'Someone owes me (Lending)')
    ]
    INTEREST_TYPES = [
        ('NONE', 'No Interest'),
        ('SIMPLE_YEARLY', 'Simple Annual Interest'),
        ('SIMPLE_MONTHLY', 'Simple Monthly Interest'),
        ('FIXED', 'Fixed Interest Amount'),
        ('EMI', 'Amortized EMI')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='debts')
    name = models.CharField(max_length=255)
    debt_type = models.CharField(max_length=20, choices=DEBT_TYPES, default='I_OWE')
    contact = models.ForeignKey(FinancialContact, on_delete=models.SET_NULL, null=True, blank=True, related_name='debts')
    
    original_principal = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    outstanding_principal = models.DecimalField(max_digits=15, decimal_places=2)
    
    interest_type = models.CharField(max_length=20, choices=INTEREST_TYPES, default='NONE')
    interest_rate = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'), help_text="Percentage or Fixed Amount")
    
    borrowing_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    expected_monthly_payment = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    is_closed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.outstanding_principal}"

class DebtPayment(models.Model):
    debt = models.ForeignKey(Debt, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    principal_allocated = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    interest_allocated = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    payment_date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment of {self.amount} for {self.debt.name}"

class IncomeSource(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='income_sources')
    name = models.CharField(max_length=255, default='Salary')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    expected_date = models.IntegerField(help_text="Day of the month (1-31)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.amount}"

class MoneyTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
        ('TRANSFER', 'Transfer'),
        ('DEBT_PAYMENT', 'Debt Payment')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    account = models.ForeignKey(MoneyAccount, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(MoneyCategory, on_delete=models.SET_NULL, null=True, blank=True)
    debt_payment = models.ForeignKey(DebtPayment, on_delete=models.SET_NULL, null=True, blank=True)
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateTimeField()
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.account:
            if self.transaction_type == 'INCOME':
                self.account.balance += self.amount
            elif self.transaction_type in ['EXPENSE', 'DEBT_PAYMENT', 'TRANSFER']:
                self.account.balance -= self.amount
            self.account.save()

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} on {self.date.date()}"

class FinancialGoal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='financial_goals')
    name = models.CharField(max_length=255)
    target_amount = models.DecimalField(max_digits=15, decimal_places=2)
    current_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    target_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class PlannedPurchase(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='planned_purchases')
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    saved_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    target_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High'), ('CRITICAL', 'Critical')], default='MEDIUM')
    affordability_status = models.CharField(max_length=50, blank=True) # e.g. "Affordable", "Save for 4 months"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
