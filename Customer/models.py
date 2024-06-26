from django.db import models
from account.models import User
from Staff.models import AccountBranches,AccountType,LoanDetail,Account
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest

class OpenAccount(models.Model):
    """
    Model representing an open account with various details such as account holder information,
    account status, documents, and transactions.

    Attributes:
        account_type (Account): ForeignKey to the Account model representing the type of account.
        mobile_number (str): The mobile number associated with the account.
        name (User): OneToOneField to the User model representing the account holder.
        date_of_birth (date): Date of birth of the account holder.
        age (int): Age of the account holder.
        status (str): Status of the account, either 'Approved' or 'Pending'.
        adhar_number (str): Aadhar number of the account holder.
        pancard_number (str): PAN card number of the account holder.
        photo (ImageField): Photo of the account holder.
        pancard_document (FileField): PAN card document of the account holder.
        adarcard_document (FileField): Aadhar card document of the account holder.
        branch (AccountBranches): ForeignKey to the AccountBranches model representing the branch of the account.
        account_number (str): Account number.
        total_amount (int): Total amount in the account.
        upi_pin (str): UPI PIN associated with the account.
    """

    APPROVED = 'Approved'
    PENDING = 'Pending'

    STATUS_CHOICES = [
        (APPROVED, 'Approved'),
        (PENDING, 'Pending'),
    ]

    account_type = models.ForeignKey(Account, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=20, unique=True)
    name = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    age = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    adhar_number = models.CharField(max_length=15, unique=True)
    pancard_number = models.CharField(max_length=20, unique=True)
    photo = models.ImageField(upload_to='account_documents')
    pancard_document = models.FileField(upload_to='account_documents', unique=True)
    adarcard_document = models.FileField(upload_to='account_documents', unique=True)
    branch = models.ForeignKey(AccountBranches, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=30, blank=True, null=True, unique=True)
    total_amount = models.PositiveIntegerField(default=0)
    upi_pin=models.CharField(max_length=6)


    @property
    def recent_deposition(self):
        """
    Returns queryset of recent deposits for this account.
    """
        return self.transaction_set.filter(deposit_amount__isnull=False)

    @property
    def recent_transfer(self):
        """
        Returns queryset of recent withdrawals for this account.
        """
        return self.transaction_set.filter(withdraw_amount__isnull=False)
    @property
    def recent_withdraw(self):
        return self.transaction_set.filter(transaction_account_number__isnull=False)
    
    @property
    def current_amount(self):
        """
        Returns the current total amount in the account.
        """
        return self.total_amount

    def __str__(self) -> str:
        return self.account_number
    
    def account_category(self):
        if self.account_type:
            return self.account_type.account_type.account_type
        return None
    
    def minimum_age_required(self):
        return self.account_type.minimum_age
    
    def minimum_age(self):
        return self.account_type.minimum_age




class Transaction(models.Model):

    """
    Model representing a transaction made by an account holder.

    Attributes:
        your_account_number (OpenAccount): ForeignKey to the OpenAccount model representing the account
                                           from which the transaction is made.
        deposit_amount (int): Amount deposited in the transaction (if any).
        withdraw_amount (int): Amount withdrawn in the transaction (if any).
        username (User): ForeignKey to the User model representing the user who initiated the transaction.
        transaction_account_number (str): Account number associated with the transaction.
    """

    your_account_number=models.ForeignKey(OpenAccount,on_delete=models.CASCADE)
    deposit_amount=models.PositiveIntegerField(null=True)
    withdraw_amount=models.PositiveIntegerField(null=True)
    username=models.ForeignKey(User,on_delete=models.CASCADE)
    transaction_account_number=models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True,null=True)  



from decimal import Decimal

class LoanApply(models.Model):

    """
    Model representing a loan application with various details such as loan amount, applicant information,
    proof of identity, address proof, and application status.

    Attributes:
        APPROVED (str): Constant representing the status 'Approved'.
        REJECTED (str): Constant representing the status 'Rejected'.
        PENDING (str): Constant representing the status 'Pending'.
        FULLY_REPAID (str): Constant representing the status 'Fully Repaid'.
        STATUS_CHOICES (list of tuples): Choices for the status field.
        loanAmount (DecimalField): The amount of the loan applied for.
        applicant_name (User): ForeignKey to the User model representing the applicant.
        PROOF_CHOICES (tuple of tuples): Choices for the proof of identity field.
        Proof_of_identity (str): The type of proof of identity provided.
        ADDRESS_CHOICES (tuple of tuples): Choices for the address proof field.
        Address_proof (str): The type of address proof provided.
        photo (ImageField): Photo uploaded with the loan application.
        salary_certificate (FileField): Salary certificate uploaded with the loan application.
        income_tax_returns (FileField): Income tax returns uploaded with the loan application.
        salary_account_statement (FileField): Salary account statement uploaded with the loan application.
        loan_application_form (FileField): Loan application form uploaded with the loan application.
        loanname (LoanDetail): ForeignKey to the LoanDetail model representing the type of loan applied for.
        status (str): Status of the loan application, one of 'Approved', 'Rejected', 'Pending', or 'Fully Repaid'.
    """


    APPROVED = 'Approved'
    REJECTED = 'Rejected'
    PENDING = 'Pending'
    FULLY_REPAID = 'Fully Repaid'

    STATUS_CHOICES = [
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (PENDING, 'Pending'),
        (FULLY_REPAID, 'Fully Repaid'),
    ]
    loanAmount = models.DecimalField(max_digits=10, decimal_places=2)
    applicant_name = models.ForeignKey(User, on_delete=models.CASCADE)
    PROOF_CHOICES = (
        ('passport', 'Passport'),
        ('VotersId', 'Voters ID'),
        ('DrivingLicence', 'Driving Licence'),
        ('PanCard', 'Pan Card')
    )
    Proof_of_identity = models.CharField(choices=PROOF_CHOICES, max_length=100)
    ADDRESS_CHOICES = (
        ('RationCard', 'Ration Card'),
        ('TelElectricityBill', 'Tel/Electricity Bill'),
        ('LeaseAgreement', 'Lease Agreement'),
        ('Passport', 'Passport')
    )
    Address_proof = models.CharField(choices=ADDRESS_CHOICES, max_length=100)
    photo = models.ImageField(upload_to='loan_application_photos', blank=True, null=True)
    salary_certificate = models.FileField(upload_to='salary_certificates', blank=True, null=True)
    income_tax_returns = models.FileField(upload_to='income_tax_returns', blank=True, null=True)
    salary_account_statement = models.FileField(upload_to='salary_account_statements', blank=True, null=True)
    loan_application_form = models.FileField(upload_to='loan_application_forms', blank=True, null=True)
    loanname = models.ForeignKey(LoanDetail, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)


    
    def interest_rate(self):
        return self.loanname.interest_rate
    
    def loan_term(self):
        return self.loanname.year

    
    def monthly_payment(self):
        """
        Calculate the monthly payment for the loan based on the loan amount, interest rate, and loan term.

        Formula: M = P * (r * (1 + r)^n) / ((1 + r)^n - 1)
        Where:
        M = monthly payment
        P = loan amount
        r = monthly interest rate (annual interest rate / 12)
        n = total number of payments (loan term * 12)
        """
        monthly_interest_rate = Decimal(self.interest_rate()) / Decimal(12 * 100)
        
        num_payments = self.loan_term() * 12
        
        monthly_payment = self.loanAmount * (monthly_interest_rate * (1 + monthly_interest_rate)**num_payments) / \
                          ((1 + monthly_interest_rate)**num_payments - 1)
        
        return monthly_payment
    def save(self, *args, **kwargs):
        """
        Save the LoanApply object to the database.
        
        Before saving, it checks if the loan amount exceeds the maximum amount allowed.
        If the loan amount is too high, it raises a ValueError.
        
        Additionally, it checks if the applicant has an account. If not, it returns an HTTP response error.
        """
        loan_detail = self.loanname
        if self.loanAmount > loan_detail.maximum_amount:
            raise ValueError("Loan amount exceeds maximum amount allowed")
        super().save(*args, **kwargs)
        
        if not self.applicant_name.has_account:
            return HttpResponseBadRequest("You have no account. Create an account.")
        
class LoanRepayment(models.Model):

    """
    Model representing a loan repayment made by an applicant.

    Attributes:
        applicant_name (User): ForeignKey to the User model representing the applicant making the repayment.
        loan_application (LoanApply): ForeignKey to the LoanApply model representing the loan application
                                      for which the repayment is made.
        amount_paid (DecimalField): The amount paid in the repayment.
        payment_date (DateField): The date when the repayment was made, auto-generated.
    """

    applicant_name = models.ForeignKey(User, on_delete=models.CASCADE)
    loan_application = models.ForeignKey('LoanApply', on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Repayment of {self.amount_paid} by {self.applicant_name.username} for loan {self.loan_application.id}"

    def save(self, *args, **kwargs):
        if self.loan_application.status != 'Approved':
            raise ValidationError("Loan status must be 'Approved' to make repayments.")
        
        
        self.loan_application.loanAmount -= self.amount_paid
        self.loan_application.save()

        super().save(*args, **kwargs)