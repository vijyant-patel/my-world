from django.db import models
from django.conf import settings
from decimal import Decimal

class Loan(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('ACTIVE', 'Active'),
        ('CLOSED', 'Closed'),
        ('DEFAULTED', 'Defaulted')
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loans')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tenure = models.IntegerField(help_text="Tenure in months")
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=12.0, help_text="Annual Interest Rate (%)")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_payable(self):
        # Simple interest for MVP: A = P(1 + rt)
        rate = Decimal(self.interest_rate) / Decimal(100)
        time = Decimal(self.tenure) / Decimal(12)
        return self.amount * (Decimal(1) + rate * time)

    def __str__(self):
        return f"Loan {self.id} - {self.user.phone} - {self.status}"

class RiskScore(models.Model):
    DECISION_CHOICES = [
        ('APPROVE', 'Approve'),
        ('REJECT', 'Reject'),
        ('MANUAL', 'Manual Review')
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='risk_score')
    score = models.IntegerField(default=0)
    decision = models.CharField(max_length=10, choices=DECISION_CHOICES, default='MANUAL')
    evaluated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Risk Score {self.score} for {self.user.phone}"
