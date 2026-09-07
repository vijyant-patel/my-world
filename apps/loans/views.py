from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import LoanSerializer, RiskScoreSerializer
from .models import Loan, RiskScore
from .utils import calculate_risk_score
from datetime import timedelta
from django.utils import timezone

class ApplyLoanView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.kyc_status != 'VERIFIED':
            return Response({"error": "KYC must be verified to apply for a loan."}, status=status.HTTP_400_BAD_REQUEST)
            
        serializer = LoanSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            tenure = serializer.validated_data['tenure']
            
            score, decision = calculate_risk_score(user, amount, tenure)
            
            # Save or update risk score
            risk_score, _ = RiskScore.objects.update_or_create(
                user=user,
                defaults={'score': score, 'decision': decision}
            )
            
            if decision == 'REJECT':
                return Response({"error": "Loan application rejected based on risk score.", "score": score}, status=status.HTTP_400_BAD_REQUEST)
            
            loan_status = 'APPROVED' if decision == 'APPROVE' else 'PENDING'
            due_date = timezone.now().date() + timedelta(days=30) if loan_status == 'APPROVED' else None
            
            loan = serializer.save(user=user, status=loan_status, due_date=due_date)
            return Response(LoanSerializer(loan).data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoanStatusView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        loans = Loan.objects.filter(user=request.user).order_by('-created_at')
        serializer = LoanSerializer(loans, many=True)
        return Response(serializer.data)

class RiskScoreView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            risk_score = RiskScore.objects.get(user=request.user)
            serializer = RiskScoreSerializer(risk_score)
            return Response(serializer.data)
        except RiskScore.DoesNotExist:
            return Response({"error": "No risk score found."}, status=status.HTTP_404_NOT_FOUND)
