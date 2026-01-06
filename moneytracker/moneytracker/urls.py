"""
URL configuration for moneytracker project.
"""
from django.contrib import admin
from django.urls import path, include
from dashboard.views import dashboard_view, dashboard_live_data
from expenses.views import (
    add_expense, add_income, add_account, add_category,
    edit_expense, delete_expense, edit_income, delete_income,
    manage_accounts, edit_account, delete_account, api_create_category,
    add_transfer, edit_transfer, delete_transfer, manage_categories, edit_category, delete_category
)
from expenses.views_budget import budget_list, budget_manage, budget_delete

from expenses.views_transactions import transactions_view, partner_transactions_view
from accounts.views_shared import shared_view, send_request, respond_request, disconnect_user
from accounts.views import register, invite_partner

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/register/', register, name='register'),
    path('accounts/partner/invite/', invite_partner, name='invite_partner'),
    path('accounts/shared/', shared_view, name='shared_view'),
    path('accounts/shared/send/', send_request, name='send_request'),
    path('accounts/shared/respond/<int:request_id>/<str:action>/', respond_request, name='respond_request'),
    path('accounts/shared/disconnect/<int:user_id>/', disconnect_user, name='disconnect_user'), 
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Dashboard URLs
    path('dashboard/', dashboard_view, name='dashboard'),
    path('dashboard/live-data/', dashboard_live_data, name='dashboard_live_data'),  # NEW: Real-time data endpoint
    
    # Transactions
    path('transactions/', transactions_view, name='transactions'),
    path('transactions/partner/', partner_transactions_view, name='partner_transactions'),
    
    # Expenses
    path('expenses/add/', add_expense, name='add_expense'),
    path('expenses/edit/<int:pk>/', edit_expense, name='edit_expense'),
    path('expenses/delete/<int:pk>/', delete_expense, name='delete_expense'),
    path('expenses/category/add/', add_category, name='add_category'),
    path('expenses/categories/', manage_categories, name='manage_categories'),
    path('expenses/categories/edit/<int:pk>/', edit_category, name='edit_category'),
    path('expenses/categories/delete/<int:pk>/', delete_category, name='delete_category'),
    
    # Income
    path('income/add/', add_income, name='add_income'),
    path('income/edit/<int:pk>/', edit_income, name='edit_income'),
    path('income/delete/<int:pk>/', delete_income, name='delete_income'),
    
    # Transfer
    path('transfer/add/', add_transfer, name='add_transfer'),
    path('transfer/edit/<int:pk>/', edit_transfer, name='edit_transfer'),
    path('transfer/delete/<int:pk>/', delete_transfer, name='delete_transfer'),

    # Accounts
    path('accounts/list/', manage_accounts, name='manage_accounts'),
    path('accounts/add/', add_account, name='add_account'),
    path('accounts/edit/<int:pk>/', edit_account, name='edit_account'),
    path('accounts/delete/<int:pk>/', delete_account, name='delete_account'),
    
    # API
    path('api/category/create/', api_create_category, name='api_create_category'),
    
    # Budget URLs
    path('budgets/', budget_list, name='budget_list'),
    path('budgets/manage/', budget_manage, name='budget_create'),
    path('budgets/manage/<str:month_str>/', budget_manage, name='budget_edit'),
    path('budgets/delete/<str:month_str>/', budget_delete, name='budget_delete'),

    # Home
    path('', dashboard_view, name='home'),
]