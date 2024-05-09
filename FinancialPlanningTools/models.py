from django.db import models
from account.models import User
from Customer.models import OpenAccount


class BudgetPlan(models.Model):

    """
        A class to represent a budget plan.

        Attributes:
            user (ForeignKey to User): The user associated with the budget plan.
            category (CharField): The category of the budget plan.
            amount (IntegerField): The amount allocated for the budget plan.
            created_at (DateTimeField): The date and time when the budget plan was created.
        """

    user=models.ForeignKey(User,on_delete=models.CASCADE)
    category=models.CharField(max_length=100)
    amount=models.IntegerField()
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    
    def __str__(self):
        return self.category


class Expenses(models.Model):
    """
    A class to represent expenses.

    Attributes:
        user (ForeignKey to User): The user associated with the expense.
        category (ForeignKey to BudgetPlan): The category of the expense.
        amount (IntegerField): The amount of the expense.
        created_at (DateTimeField): The date and time when the expense was created.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)  
    category = models.ForeignKey(BudgetPlan, on_delete=models.CASCADE)
    amount = models.IntegerField()
    created_at=models.DateTimeField(auto_now_add=True,null=True)



    def __str__(self):
        return f"Expense: {self.category.category}, Amount: {self.amount}"
    
class SavingsGoal(models.Model):

    """
        A class to represent a savings goal.

        Attributes:
            user (ForeignKey to User): The user associated with the savings goal.
            name (CharField): The name of the savings goal.
            target_amount (DecimalField): The target amount to be saved for the goal.
            current_amount (ForeignKey to OpenAccount): The current amount saved for the goal.
            deadline (DateField): The deadline for achieving the savings goal (optional).
            completed (BooleanField): Indicates whether the savings goal has been completed.
            created_at (DateTimeField): The date and time when the savings goal was created.
        """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.ForeignKey(OpenAccount,on_delete=models.CASCADE)
    deadline = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True,null=True)