from decimal import Decimal

def calculate_risk_score(user, loan_amount, tenure):
    score = 0
    decision = 'MANUAL'
    
    if not user.salary:
        return 0, 'REJECT'
        
    salary = Decimal(user.salary)
    amount = Decimal(loan_amount)
    
    # Rule 1: Salary >= 25000
    if salary >= 25000:
        score += 40
    else:
        return 0, 'REJECT'
        
    # Rule 2: EMI < 40% of salary
    # Simple EMI calculation for MVP: Total / tenure
    rate = Decimal('0.12') # 12%
    time = Decimal(tenure) / Decimal(12)
    total_payable = amount * (Decimal(1) + rate * time)
    emi = total_payable / Decimal(tenure)
    
    if emi < (salary * Decimal('0.40')):
        score += 40
    else:
        return 20, 'REJECT'
        
    # Rule 3: No recent payment bounce (mocked)
    score += 20
    
    if score >= 80:
        decision = 'APPROVE'
        
    return score, decision
