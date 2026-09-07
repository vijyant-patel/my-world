from django.contrib import admin
from .models import Repayment

class RepaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'loan', 'amount_paid', 'status', 'date')
    list_filter = ('status',)

admin.site.register(Repayment, RepaymentAdmin)
