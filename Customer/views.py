from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import OpenAccountSerializer,DepositeSerializer,LoanApplySerializer,MyAccountSerializer,FundTransferViewSerializer, WithdrawSerializer
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser, JSONParser
from django.core.mail import send_mail
from .models import *
from django.conf import settings
from django.db.models import Sum
from django.db.models import Prefetch
from rest_framework.exceptions import PermissionDenied
from Staff.serializers import LoanDetailSerializer
from django.http import Http404
from Staff.serializers import AccountSerializer,LoanSerializer,BranchSerializer
from rest_framework.exceptions import APIException
from rest_framework import generics
from django.utils import timezone
from datetime import timedelta
from .serializers import LoanApplyEditDeleteSerializer,LoanEditSerializer,LoanRepaymentSerializer
from rest_framework.exceptions import PermissionDenied as CustomPermissionDenied
from Staff.models import AccountBranches




class AccountListView(generics.ListAPIView):
    """
    API view for listing all account details.
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]  

class BranchListView(generics.ListAPIView):
    """
    API view for listing all account details.
    """
    queryset = AccountBranches.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated]  


class LoanListView(generics.ListAPIView):
    """
    API view for listing all account details.
    """
    queryset =LoanDetail.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]  

class OpenAccountView(APIView):
    """
    API view for opening a new account.
    
    This view allows authenticated users to apply for a new account. Upon successful application,
    an email notification is sent to the staff.

    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, FileUploadParser, JSONParser)
    
    def post(self, request, format=None):
        """
        Handle POST request for opening a new account.
        
        Args:
            request (HttpRequest): The HTTP request object.
            format (str): The format of the request data.
        
        Returns:
            Response: HTTP response indicating the result of the account opening attempt.
        """
        user = request.user
        request.data['name'] = user.id
        
        open_accounts = OpenAccount.objects.select_related('account_type').prefetch_related(Prefetch('account_type', queryset=Account.objects.only('minimum_age')))

        serializer = OpenAccountSerializer(data=request.data)
        if serializer.is_valid():
            account_type = serializer.validated_data.get('account_type')
            print(account_type)
            minimum_age = account_type.minimum_age

            if minimum_age > serializer.validated_data['age']:
                return Response({"error": "User does not meet the minimum age requirement for this account type."}, status=status.HTTP_400_BAD_REQUEST)

            if request.user.has_account:
                return Response({"error": "User already has an account"}, status=status.HTTP_400_BAD_REQUEST)
            account_instance = serializer.save(name=user)
            user.has_account = True
            user.save()
            
            subject = 'New account application'
            message = f"A new account application has been submitted.\n\n\
                Name: {serializer.data['name']}\n\
                Adarnumber: {serializer.data['adhar_number']}\n\
                Pancard number: {serializer.data['pancard_number']}\n\
                Branch: {serializer.data['branch']}\n\
                Account type: {serializer.data['account_type']}"
            admin_email = 'admin@example.com'  # Replace with the admin's email address
            send_mail(subject, message, admin_email, [admin_email])

            return Response({"message": "Your application for opening a new account has been submitted. \
                An email containing your account number will be sent to your email address after verification.","data": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyAccount(APIView):
    """
    API view for retrieving account information of the authenticated user.

    This view retrieves account details for the authenticated user. It fetches
    the OpenAccount object associated with the user and serializes the data
    to be returned as a response.

    Permissions:
    - The user must be authenticated to access this view.

    HTTP Methods:
    - GET: Retrieves the account information for the authenticated user.

    Args:
    - request (HttpRequest): The HTTP request object.
    - format (str, optional): The format of the response data. Defaults to None.

    Returns:
    - Response: HTTP response containing the serialized account data.
               If the account is not found for the user, returns an error response
               with status code 404.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, format=None):
        try:
            account = OpenAccount.objects.select_related('account_type').get(name=request.user)
        except OpenAccount.DoesNotExist:
            return Response({"error": "Account not found for this user"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MyAccountSerializer(account)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EditAccountView(APIView):
    """
    API view for editing an existing account.

    This view allows authenticated users to edit their account details.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk, format=None):
        """
        Handle PUT request to update an existing account.

        Args:
            request (HttpRequest): The HTTP request object.
            pk (int): The primary key of the account to be updated.
            format (str): The format of the request data.

        Returns:
            Response: HTTP response indicating the result of the update operation.
        """
        try:
            account = OpenAccount.objects.select_related('branch', 'account_type').get(pk=pk)

            if request.user != account.name:
                return Response({"error": "You are not authorized to edit this account"}, status=status.HTTP_403_FORBIDDEN)
            
            serializer = OpenAccountSerializer(account, data=request.data, partial=True)  
            if serializer.is_valid():
                account_type = serializer.validated_data.get('account_type')
                if account_type:
                    minimum_age = account_type.minimum_age
                    age=serializer.validated_data.get('age')
                    if age is not None and minimum_age > age:
                        return Response({"error": "User does not meet the minimum age requirement for this account type."}, status=status.HTTP_400_BAD_REQUEST)

                serializer.save()




                subject = 'accounted edited'
                message = f"your account is edited.\n\n\
                    Name: {serializer.data['name']}\n\
                    Adarnumber: {serializer.data['adhar_number']}\n\
                    Pancard number: {serializer.data['pancard_number']}\n\
                    Branch: {serializer.data['branch']}\n\
                    Account type: {serializer.data['account_type']}"
                admin_email = 'admin@example.com'  
                send_mail(subject, message, admin_email, [admin_email])

                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except OpenAccount.DoesNotExist:
            return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DepositeAmountView(APIView):
    """
    API view for depositing an amount into a user's account.

    This view allows authenticated users to deposit an amount into their account. Upon successful deposit,
    a transaction record is created and the account's total amount is updated.

    Attributes:
        authentication_classes (list): List of authentication classes.
        permission_classes (list): List of permission classes.
    
    Methods:
        post: Handles POST request for depositing an amount into the user's account.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        """
        Handle POST request for depositing an amount into the user's account.

        Args:
            request (HttpRequest): The HTTP request object.
            format (str, optional): The format of the request data.

        Returns:
            Response: HTTP response indicating the result of the deposit attempt.
        """
        serializer = DepositeSerializer(data=request.data)
        if serializer.is_valid():
            your_account_number = request.data.get('your_account_number')
            if not your_account_number:
                return Response({"error": "Account number is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                account = OpenAccount.objects.select_related('name').get(account_number=your_account_number)
            except OpenAccount.DoesNotExist:
                return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
            
            if request.user != account.name:
                return Response({"error": "You are not authorized to perform this transaction"}, status=status.HTTP_403_FORBIDDEN)
            
            deposit_amount = serializer.validated_data.get('deposit_amount')
            
            if deposit_amount is not None:
                new_balance = account.total_amount + deposit_amount
            else:
                return Response({"error": "Deposit amount must be provided"}, status=status.HTTP_400_BAD_REQUEST)
                        
            transaction = serializer.save(username=request.user, your_account_number=account)
            account.total_amount = new_balance
            account.save()
            return Response(DepositeSerializer(transaction).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FundTransferView(APIView):
    """
    API view for withdrawing an amount from the user's account.

    This view allows authenticated users to withdraw a specified amount from their account.
    """

    def post(self, request, format=None):
        """
        Handle POST request for withdrawing an amount from the user's account.

        Args:
            request (HttpRequest): The HTTP request object.
            format (str): The format of the request data.

        Returns:
            Response: HTTP response indicating the result of the withdrawal attempt.
        """
        serializer = FundTransferViewSerializer(data=request.data)
        if serializer.is_valid():

            your_account_number = serializer.validated_data.get('your_account_number')
            try:
                account = OpenAccount.objects.select_related('account_type').get(account_number=your_account_number)
            except OpenAccount.DoesNotExist:
                return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
            if request.user != account.name:
                return Response({"error": "You are not authorized to perform this transaction"}, status=status.HTTP_403_FORBIDDEN)
            withdraw_amount = serializer.validated_data.get('withdraw_amount')
            upi_pin=serializer.validated_data.get('upi_pin')
            if withdraw_amount <= 0:
                return Response({"error": "Invalid withdraw amount"}, status=status.HTTP_400_BAD_REQUEST)
            if account.total_amount < withdraw_amount:
                return Response({"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)
            
            if your_account_number==serializer.validated_data.get('transaction_account_number'):
                return Response({"error": "both account number are same cant proceed the transaction"}, status=status.HTTP_400_BAD_REQUEST)


            twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
            total_withdrawals_last_24_hours = Transaction.objects.filter(
            username=request.user,
            created_at__gte=twenty_four_hours_ago,
            ).aggregate(total_withdrawals=Sum('withdraw_amount'))['total_withdrawals'] or 0

            if account.account_type.maximum_transaction_amount_per_day < (total_withdrawals_last_24_hours + withdraw_amount):
                return Response({"error": "Cannot transfer this much amount within 24 hours"}, status=status.HTTP_400_BAD_REQUEST)
            
            if account.upi_pin != upi_pin:
                return Response({"error": "wrong upi pin"}, status=status.HTTP_400_BAD_REQUEST)

            new_balance = account.total_amount - withdraw_amount
            if new_balance < account.account_type.minimum_balance:
                return Response({"error": "Your account balance is below the minimum required balance. We will credit a certain amount to keep your account balance sufficient."}, status=status.HTTP_400_BAD_REQUEST)
            transaction = Transaction.objects.create(
                your_account_number=account,
                withdraw_amount=withdraw_amount,
                username=request.user,
                transaction_account_number=serializer.validated_data.get('transaction_account_number')
            )
            try:
                transaction_account = OpenAccount.objects.get(account_number=transaction.transaction_account_number)
            except OpenAccount.DoesNotExist:
                return Response({"error": "Transaction account not found"}, status=status.HTTP_404_NOT_FOUND)
            transaction_account.total_amount += withdraw_amount
            transaction_account.save()
            account.total_amount = new_balance
            account.save()
            return Response({
            "success": "Withdrawal successful",
            "new_balance": new_balance,
            "created_at": transaction.created_at}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WithdrawView(APIView):
    """
    API view for withdrawing an amount from the user's account.

    This view allows authenticated users to withdraw a specified amount from their account.
    """

    def post(self, request, format=None):
        """
        Handle POST request for withdrawing an amount from the user's account.

        Args:
            request (HttpRequest): The HTTP request object.
            format (str): The format of the request data.

        Returns:
            Response: HTTP response indicating the result of the withdrawal attempt.
        """
        serializer = WithdrawSerializer(data=request.data)
        if serializer.is_valid():
            account_number = serializer.validated_data.get('your_account_number')
            withdraw_amount = serializer.validated_data.get('withdraw_amount')
            upi_pin = serializer.validated_data.get('upi_pin')

            try:
                account = OpenAccount.objects.get(account_number=account_number)
            except OpenAccount.DoesNotExist:
                return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)

            if request.user != account.name:
                return Response({"error": "You are not authorized to perform this transaction"}, status=status.HTTP_403_FORBIDDEN)

            if withdraw_amount <= 0:
                return Response({"error": "Invalid withdraw amount"}, status=status.HTTP_400_BAD_REQUEST)

            if account.total_amount < withdraw_amount:
                return Response({"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)

            if account.upi_pin != upi_pin:
                return Response({"error": "Wrong UPI PIN"}, status=status.HTTP_400_BAD_REQUEST)

            new_balance = account.total_amount - withdraw_amount

            if new_balance < account.account_type.minimum_balance:
                return Response({"error": "Your account balance is below the minimum required balance."}, status=status.HTTP_400_BAD_REQUEST)

            twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
            total_withdrawals_last_24_hours = Transaction.objects.filter(
                username=request.user,
                created_at__gte=twenty_four_hours_ago,
            ).aggregate(total_withdrawals=Sum('withdraw_amount'))['total_withdrawals'] or 0

            if account.account_type.maximum_transaction_amount_per_day < (total_withdrawals_last_24_hours + withdraw_amount):
                return Response({"error": "Cannot withdraw this much amount within 24 hours"}, status=status.HTTP_400_BAD_REQUEST)

            transaction = Transaction.objects.create(
                your_account_number=account,
                withdraw_amount=withdraw_amount,
                username=request.user,
            )

            account.total_amount = new_balance
            account.save()

            return Response({
                "success": "Withdrawal successful",
                "new_balance": new_balance,
                "created_at": transaction.created_at
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoanApplyView(APIView):
    """
    Endpoint for applying for a loan.
    """
    def post(self, request, format=None):
        if not request.user.has_account:
            raise PermissionDenied("You need to create an account first before applying for a loan.")
        if  request.user.has_loan:
            raise PermissionDenied("You already have a loan. After the payment, apply for a new loan.")
        serializer = LoanApplySerializer(data=request.data)
        if serializer.is_valid():
            loan_application = serializer.save(applicant_name=request.user)
            loan_detail_serializer = LoanDetailSerializer(loan_application.loanname)
            monthly_payment = loan_application.monthly_payment()  
            response_data = {
                "success": "Loan application submitted successfully",
                "loan_application": serializer.data,
                "loan_detail": loan_detail_serializer.data,
                "monthly_payment": monthly_payment
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        return Response({"error": "GET method not allowed for this endpoint"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def put(self, request, format=None):
        return Response({"error": "PUT method not allowed for this endpoint"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, request, format=None):
        return Response({"error": "DELETE method not allowed for this endpoint"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CustomPermissionDenied(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to access this loan application.'
    default_code = 'permission_denied'


class LoanRepaymentView(APIView):
   


    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


    """
    API view for repaying a loan.

    This view allows authenticated users to repay their approved loan amount.

    Authentication:
        Requires JWT authentication.

    Permissions:
        Requires the user to be authenticated.

    HTTP Methods Allowed: POST
    """

    def post(self, request):
        serializer = LoanRepaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['applicant_name'] = request.user

            try:
                user = request.user
                loan_applications = LoanApply.objects.filter(applicant_name=user).select_related('applicant_name')

                approved_loan_applications = loan_applications.filter(status=LoanApply.APPROVED)
                if not approved_loan_applications.exists():
                    return Response({"error": "No approved loan application found for repayment"},
                                    status=status.HTTP_400_BAD_REQUEST)

                amount_paid = serializer.validated_data.get('amount_paid')

                if amount_paid <= 0:
                    return Response({"error": "Repayment amount must be greater than zero"},
                                    status=status.HTTP_400_BAD_REQUEST)

                for loan_application in approved_loan_applications:
                    if amount_paid > loan_application.loanAmount:
                        return Response({"error": "Repayment amount exceeds total loan amount"},
                                        status=status.HTTP_400_BAD_REQUEST)

                    remaining_balance = loan_application.loanAmount - amount_paid

                    if remaining_balance < 0:
                        return Response({"error": "Repayment amount exceeds total remaining loan balance"},
                                        status=status.HTTP_400_BAD_REQUEST)

                if remaining_balance == 0:
                    loan_application.status = LoanApply.FULLY_REPAID
                    loan_application.loanAmount=0
                    loan_application.save()
                    loan_application.applicant_name.has_loan = False
                    loan_application.applicant_name.save()
                else:
                        serializer.save()


 
                return Response({"success": "Repayment processed successfully",
                                 "remaining_balance": remaining_balance},
                                status=status.HTTP_201_CREATED)
                print(loan_application.status)
            except LoanApply.DoesNotExist:
                return Response({"error": "No loan application found for repayment"},
                                status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class LoanEditDeleteView(APIView):
    permission_classes = [IsAuthenticated]  
    def get_object(self, pk):
        try:
            loan_application = LoanApply.objects.get(pk=pk)
            if loan_application.applicant_name != self.request.user:
                raise CustomPermissionDenied("You do not have permission to access this loan application.")
            return loan_application
        except LoanApply.DoesNotExist:
            raise Http404("Loan application not found")

    def get(self, request, pk, format=None):
        loan_application = self.get_object(pk)
        serializer = LoanApplyEditDeleteSerializer(loan_application)
        loan_detail_serializer = LoanDetailSerializer(loan_application.loanname)
        monthly_payment = loan_application.monthly_payment()  
        response_data = {
            "loan_application": serializer.data,
            "loan_detail": loan_detail_serializer.data,
            "monthly_payment": monthly_payment
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        """
        Update a loan application.
        """
        loan_application = self.get_object(pk)
        if loan_application.status == 'Approved':
            raise PermissionDenied("You cannot edit the loan application after it has been approved.")
        if request.user.id != loan_application.applicant_name.id:
            return Response({"error": "You do not have permission to edit this data."}, status=status.HTTP_403_FORBIDDEN)

        
        serializer = LoanEditSerializer(loan_application, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        """
        Delete a loan application.
        """
        loan_application = self.get_object(pk)
        if loan_application.status == 'Approved':
            raise PermissionDenied("You cannot delete the loan application after it has been approved.")
        if request.user.id != loan_application.applicant_name.id:
            return Response({"error": "You do not have permission to delete the application."}, status=status.HTTP_403_FORBIDDEN)

        
        loan_application.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
