"""
URL configuration for moneytracker project.
"""
from django.contrib import admin
from django.urls import path, include
from dashboard.views import dashboard_view
from expenses.views import (
    add_expense, add_income, add_account, add_category,
    edit_expense, delete_expense, edit_income, delete_income,
    manage_accounts, edit_account, delete_account, api_create_category
)

from expenses.views_transactions import transactions_view, partner_transactions_view
from accounts.views_couple import couple_view
from accounts.views import register, invite_partner

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/register/', register, name='register'),
    path('accounts/partner/invite/', invite_partner, name='invite_partner'),
    path('accounts/couple/', couple_view, name='couple_view'), 
    path('accounts/', include('django.contrib.auth.urls')),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('transactions/', transactions_view, name='transactions'),
    path('transactions/partner/', partner_transactions_view, name='partner_transactions'),
    path('expenses/add/', add_expense, name='add_expense'),
    path('expenses/edit/<int:pk>/', edit_expense, name='edit_expense'),
    path('expenses/delete/<int:pk>/', delete_expense, name='delete_expense'),
    path('expenses/category/add/', add_category, name='add_category'),
    path('income/add/', add_income, name='add_income'),
    path('income/edit/<int:pk>/', edit_income, name='edit_income'),
    path('income/delete/<int:pk>/', delete_income, name='delete_income'),
    path('accounts/list/', manage_accounts, name='manage_accounts'),
    path('accounts/add/', add_account, name='add_account'),
    path('accounts/edit/<int:pk>/', edit_account, name='edit_account'),
    path('accounts/delete/<int:pk>/', delete_account, name='delete_account'),
    path('api/category/create/', api_create_category, name='api_create_category'),

    path('', dashboard_view, name='home'),
]
