from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from .models import BudgetPlan,SavingsGoal,Expenses
from .serializers import BudgetPlanSerializer,ExpenseSerializer,SavingsGoalSerializer
from rest_framework.exceptions import NotFound
import logging
from Customer.models import OpenAccount
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from django.contrib import messages
from rest_framework import viewsets, status

from datetime import datetime

class BudgetPlanView(APIView):
    """
    API view for adding or updating budget plan details.
    
    This view allows authenticated users to add or update budget plan details for the current month.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        """
        Handle POST request for adding or updating budget plan details.
        
        Args:
            request (HttpRequest): The HTTP request object.
            format (str): The format of the request data.
        
        Returns:
            Response: HTTP response indicating the result of the budget plan addition or update attempt.
        """
        try:
            if not request.user.is_authenticated:
                raise AuthenticationFailed("Authentication credentials were not provided.")

            serializer = BudgetPlanSerializer(data=request.data)
            if serializer.is_valid():
                current_month = datetime.now().month
                current_year = datetime.now().year
                
                existing_budget_plan = BudgetPlan.objects.select_related('user').filter(
                    user=request.user,
                    category=serializer.validated_data['category'],
                    created_at__month=current_month,
                    created_at__year=current_year
                ).first()

                if existing_budget_plan:
                    existing_budget_plan.amount = serializer.validated_data['amount']
                    existing_budget_plan.save()
                    return Response({"message": "Budget plan is exsting so just updating the details  successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    serializer.save(user=request.user)
                    return Response({"message": "Budget plan details added successfully.", "data": serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except AuthenticationFailed:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)


        
        
        
class BudgetPlanDetailView(APIView):
    """
    API view for updating and deleting budget plan details.
    
    This view allows authenticated users to update and delete their existing budget plans.
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return BudgetPlan.objects.get(pk=pk, user=self.request.user)
        except BudgetPlan.DoesNotExist:
            raise NotFound("Budget plan not found.")

    def put(self, request, pk, format=None):
        """
        Handle PUT request for updating budget plan details.
        
        Args:
            request (HttpRequest): The HTTP request object.
            pk (int): The primary key of the budget plan to update.
            format (str): The format of the request data.
        
        Returns:
            Response: HTTP response indicating the result of the budget plan update attempt.
        """
        try:
            budget_plan = self.get_object(pk)
            serializer = BudgetPlanSerializer(budget_plan, data=request.data, partial=True)  
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Budget plan details updated successfully.", "data": serializer.data})
            else:
                return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk, format=None):
        """
        Handle DELETE request for deleting budget plan details.
        
        Args:
            request (HttpRequest): The HTTP request object.
            pk (int): The primary key of the budget plan to delete.
            format (str): The format of the request data.
        
        Returns:
            Response: HTTP response indicating the result of the budget plan deletion attempt.
        """
        try:
            budget_plan = self.get_object(pk)
            budget_plan.delete()
            return Response({"message": "Budget plan deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

class UserBudgetPlansView(APIView):
    """
    API view for retrieving all budget plans added by the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """
        Handle GET request to retrieve all budget plans added by the authenticated user.
        
        Args:
            request (HttpRequest): The HTTP request object.
            format (str): The format of the request data.
        
        Returns:
            Response: HTTP response containing the budget plans added by the authenticated user.
        """
        try:
            user_budget_plans = BudgetPlan.objects.filter(user=request.user)
            
            if not user_budget_plans:
                return Response({"message": "No budget plans found for the authenticated user."}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = BudgetPlanSerializer(user_budget_plans, many=True)
            
            response_data = {
                "message": f"Retrieved {len(user_budget_plans)} budget plans for the authenticated user.",
                "count": len(user_budget_plans),
                "budget_plans": serializer.data
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from datetime import datetime

class AddExpenseView(APIView):
    """
    API view for adding expenses.
    
    This view allows authenticated users to add expenses.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        """
        Handle POST request for adding expenses.
        
        Args:
            request (HttpRequest): The HTTP request object.
            format (str): The format of the request data.
        
        Returns:
            Response: HTTP response indicating the result of the expense addition attempt.
        """
        try:
            category_id = request.data.get('category')
            if category_id is None:
                return Response({"error": "Please provide a category ID."}, status=status.HTTP_400_BAD_REQUEST)

            budget_plan = BudgetPlan.objects.filter(pk=category_id, user=request.user).first()
            if budget_plan is None:
                return Response({"error": "Invalid category ID or category does not belong to you."}, status=status.HTTP_400_BAD_REQUEST)
            
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            existing_expense = Expenses.objects.filter(
                category_id=category_id,
                created_at__month=current_month,
                created_at__year=current_year
            ).first()

            serializer = ExpenseSerializer(data=request.data)
            if serializer.is_valid():
                if existing_expense:
                    existing_expense.amount += serializer.validated_data['amount']
                    existing_expense.save()
                    if existing_expense.amount > budget_plan.amount:
                        return Response({"message": "Expense amount exceeds the budget plan amount.", "data": serializer.data}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({"message": "Expense amount updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    serializer.save()
                    return Response({"message": "Expense added successfully.", "data": serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logging.exception("An error occurred while adding the expense:")
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ListExpensesView(generics.ListAPIView):
    """
    API view for listing all expenses of the logged-in user.
    """

    serializer_class = ExpenseSerializer

    def get_queryset(self):
        return Expenses.objects.filter(category__user=self.request.user)
    

class RetrieveUpdateDestroyExpenseView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a specific expense.
    """
    permission_classes = [IsAuthenticated]
    queryset = Expenses.objects.all()
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        return self.queryset.filter(category__user=self.request.user)

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs.get('pk'))
        return obj

    def update(self, request, *args, **kwargs):
        """
        Handle partial update (PATCH) request for updating the expense data.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Expense updated successfully."}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        Handle DELETE request for deleting the expense.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Expense deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs):
        """
        Handle GET request for retrieving the expense.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"message": "Expense retrieved successfully.", "data": serializer.data}, status=status.HTTP_200_OK)



# class SavingsGoalCreateView(APIView):
#     def post(self, request):
#         try:
#             target_amount = int(request.data.get('target_amount'))
            
#             open_account = OpenAccount.objects.get(name=request.user.id)
#             total_amount = open_account.total_amount

#             if target_amount <= total_amount:
#                 serializer = SavingsGoalSerializer(data=request.data)
#                 if serializer.is_valid():
#                     serializer.save(user=request.user, current_amount=open_account)
#                     return Response({"message": "Savings goal created successfully."}, status=status.HTTP_201_CREATED)
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 return Response({"error": "Target amount exceeds total available amount."}, status=status.HTTP_400_BAD_REQUEST)
#         except OpenAccount.DoesNotExist:
#             return Response({"error": "OpenAccount not found for the authenticated user."}, status=status.HTTP_404_NOT_FOUND)
#         except ValueError:
#             return Response({"error": "Invalid target amount. Please provide a valid integer value."}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({"error": "An error occurred while processing the request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from django.core.mail import send_mail
from django.conf import settings

class SavingsGoalCreateView(APIView):
    def post(self, request):
        try:
            target_amount = int(request.data.get('target_amount'))
            
            open_account = OpenAccount.objects.get(name=request.user.id)
            total_amount = open_account.total_amount

            serializer = SavingsGoalSerializer(data=request.data)
            if serializer.is_valid():
                savings_goal = serializer.save(user=request.user, current_amount=open_account)

                if total_amount >= target_amount:
                    # Send email notification
                    send_mail(
                        'Savings Goal Achieved',
                        f'Congratulations! You have achieved your savings goal of {target_amount}.',
                        settings.EMAIL_HOST_USER,  # From email address
                        [request.user.email],  # To email address
                        fail_silently=False,
                    )
                else:
                    # Send encouragement message if target amount is greater than available amount
                    send_mail(
                        'Savings Goal Update',
                        f'You are currently {target_amount - total_amount} ruppes away from your savings goal of {target_amount}. Keep saving and best of luck!',
                        settings.EMAIL_HOST_USER,  # From email address
                        [request.user.email],  # To email address
                        fail_silently=False,
                    )

                return Response({"message": "Savings goal created successfully."}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except OpenAccount.DoesNotExist:
            return Response({"error": "OpenAccount not found for the authenticated user."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({"error": "Invalid target amount. Please provide a valid integer value."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "An error occurred while processing the request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class SavingsGoalViewSet(viewsets.ModelViewSet):
    queryset = SavingsGoal.objects.all()
    
    serializer_class = SavingsGoalSerializer
    
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

        
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        messages.success(request, "Savings goal updated successfully.")
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        messages.success(request, "Savings goal deleted successfully.")
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()
