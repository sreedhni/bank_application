from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'savings-goals', views.SavingsGoalViewSet, basename='savings-goal')

urlpatterns = [
    path('add-budget/', views.BudgetPlanView.as_view()),
    path('budget-plans/<int:pk>/', views.BudgetPlanDetailView.as_view(), name='budget-plan-detail'),
    path('user-budget-plans/', views.UserBudgetPlansView.as_view(), name='user-budget-plans'),
    path('add-expense/', views.AddExpenseView.as_view(), name='add-expense'),
    path('expenses/', views.ListExpensesView.as_view(), name='list-expenses'),
    path('expenses/<int:pk>/', views.RetrieveUpdateDestroyExpenseView.as_view(), name='expense-detail'),
    path('add/savings/', views.SavingsGoalCreateView.as_view(), name='savings-goal-list-create'),
    path('', include(router.urls)),
]
