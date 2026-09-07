from django.contrib import admin
from .models import Loan, RiskScore

class LoanAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'status', 'created_at')
    list_filter = ('status',)

class RiskScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'decision')

admin.site.register(Loan, LoanAdmin)
admin.site.register(RiskScore, RiskScoreAdmin)
