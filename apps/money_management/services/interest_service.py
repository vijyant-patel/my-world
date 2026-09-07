from decimal import Decimal, ROUND_HALF_UP

class InterestService:
    @staticmethod
    def calculate_simple_yearly(principal: Decimal, rate: Decimal, days: int) -> Decimal:
        """
        Calculates Simple Annual Interest based on number of days.
        Formula: Interest = P * R * T (T in years)
        """
        if principal <= 0 or rate <= 0 or days <= 0:
            return Decimal('0.00')
        years = Decimal(days) / Decimal('365')
        interest = principal * (rate / Decimal('100')) * years
        return interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @staticmethod
    def calculate_simple_monthly(principal: Decimal, rate: Decimal, months: int) -> Decimal:
        """
        Calculates Simple Monthly Interest.
        rate is per month.
        """
        if principal <= 0 or rate <= 0 or months <= 0:
            return Decimal('0.00')
        interest = principal * (rate / Decimal('100')) * Decimal(months)
        return interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @staticmethod
    def calculate_emi(principal: Decimal, yearly_rate: Decimal, tenure_months: int) -> Decimal:
        """
        Calculates Equated Monthly Installment (EMI).
        Formula: EMI = P * r * (1+r)^n / ((1+r)^n - 1)
        r = monthly interest rate
        n = tenure in months
        """
        if principal <= 0 or tenure_months <= 0:
            return Decimal('0.00')
        if yearly_rate <= 0:
            return (principal / Decimal(tenure_months)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
        r = (yearly_rate / Decimal('100')) / Decimal('12')
        n = Decimal(tenure_months)
        
        one_plus_r_to_n = (Decimal('1') + r) ** n
        emi = principal * r * one_plus_r_to_n / (one_plus_r_to_n - Decimal('1'))
        
        return emi.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
    @staticmethod
    def calculate_interest_for_debt(debt, days: int = 30) -> Decimal:
        """
        Helper to calculate upcoming interest for a given debt record based on its type.
        """
        if debt.interest_type == 'NONE':
            return Decimal('0.00')
        elif debt.interest_type == 'SIMPLE_YEARLY':
            return InterestService.calculate_simple_yearly(debt.outstanding_principal, debt.interest_rate, days)
        elif debt.interest_type == 'SIMPLE_MONTHLY':
            # roughly map days to months
            months = max(1, days // 30)
            return InterestService.calculate_simple_monthly(debt.outstanding_principal, debt.interest_rate, months)
        elif debt.interest_type == 'FIXED':
            # fixed amount, assuming it's an upfront fee added to principal, 
            # so ongoing interest is 0.
            return Decimal('0.00')
        elif debt.interest_type == 'EMI':
            # Monthly interest portion of EMI = outstanding_principal * (yearly_rate / 12)
            if debt.interest_rate > 0:
                monthly_rate = (debt.interest_rate / Decimal('100')) / Decimal('12')
                interest = debt.outstanding_principal * monthly_rate
                return interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            return Decimal('0.00')
        return Decimal('0.00')
