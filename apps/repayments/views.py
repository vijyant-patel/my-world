from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import RepaymentSerializer
from apps.loans.models import Loan
import uuid

class PayRepaymentView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RepaymentSerializer(data=request.data)
        if serializer.is_valid():
            loan = serializer.validated_data['loan']
            amount_paid = serializer.validated_data['amount_paid']
            
            if loan.user != request.user:
                return Response({"error": "Not authorized to pay this loan."}, status=status.HTTP_403_FORBIDDEN)
                
            if loan.status not in ['ACTIVE', 'APPROVED', 'DEFAULTED']:
                return Response({"error": f"Cannot make payment for loan in {loan.status} status."}, status=status.HTTP_400_BAD_REQUEST)
                
            # Mock payment gateway success
            transaction_id = f"txn_{uuid.uuid4().hex[:10]}"
            
            repayment = serializer.save(
                status='COMPLETED', 
                transaction_id=transaction_id
            )
            
            # Simple logic: If paid amount >= total_payable, close loan
            # MVP logic, assuming one-time payment for simplicity
            if amount_paid >= loan.total_payable:
                loan.status = 'CLOSED'
                loan.save()
            else:
                loan.status = 'ACTIVE'
                loan.save()
                
            return Response(RepaymentSerializer(repayment).data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
