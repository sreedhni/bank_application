from django.db import models
from account.models import User
from Customer.models import OpenAccount


class BudgetPlan(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    category=models.CharField(max_length=100)
    amount=models.IntegerField()
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    
    def __str__(self):
        return self.category


class Expenses(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)  
    category = models.ForeignKey(BudgetPlan, on_delete=models.CASCADE)
    amount = models.IntegerField()
    created_at=models.DateTimeField(auto_now_add=True,null=True)



    def __str__(self):
        return f"Expense: {self.category.category}, Amount: {self.amount}"
    
class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.ForeignKey(OpenAccount,on_delete=models.CASCADE)
    deadline = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True,null=True)