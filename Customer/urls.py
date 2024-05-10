from django.urls import path
from Customer import views


urlpatterns = [path('account-application/',views.OpenAccountView.as_view(),name="open-account"),
 path('allaccountdetails/', views.AccountListView.as_view(), name='all-account'),   
 path('allloandetails/', views.LoanListView.as_view(), name='all-loan'), 
  path('allbranchdetails/', views.BranchListView.as_view(), name='all-branch'),   
  

 path('accounts/<int:pk>/edit/', views.EditAccountView.as_view(), name='edit_account'),   
 path('my-account/', views.MyAccount.as_view(), name='my-account'),
 path('deposit/', views.DepositeAmountView.as_view(), name='transaction-list'),   
 path('loan-apply/', views.LoanApplyView.as_view(), name='loan_apply'),
 path('fundtransfer/', views.FundTransferView.as_view(), name='transfer'),  
 path('withdraw/',views.WithdrawView.as_view(),name='withdraw'),
 path('repayment/', views.LoanRepaymentView.as_view(), name='loan-repayment'),

path('loan-application/<int:pk>/', views.LoanEditDeleteView.as_view(), name='loan-application-edit'),

        
]
