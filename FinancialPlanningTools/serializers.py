from rest_framework import serializers
from .models import BudgetPlan,Expenses,SavingsGoal

class BudgetPlanSerializer(serializers.ModelSerializer):

    """
    Serializer for BudgetPlan model.
    """
    class Meta:
        model = BudgetPlan
        fields = ['id','category', 'amount']

class ExpenseSerializer(serializers.ModelSerializer):
    """
    A serializer class for serializing Expenses objects.

    Attributes:
        budget_planed (CharField): The amount allocated in the budget plan category for the expense (read-only).
    """
    budget_planed=serializers.CharField(source='category.amount',read_only=True)
    class Meta:
        model = Expenses
        fields = ["id",'category', 'amount',"budget_planed"]


class SavingsGoalSerializer(serializers.ModelSerializer):
    account_balance=serializers.CharField(source='current_amount.total_amount',read_only=True)
    user=serializers.CharField(source='user.name',read_only=True)

    class Meta:
        model = SavingsGoal
        fields = ['id', 'user', 'name', 'target_amount','completed','account_balance']
        read_only_fields = ['user', 'completed']
