from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from expenses.models import Expense, Income, Budget, BankAccount
from django.db.models import Sum
import json
from django.core.serializers.json import DjangoJSONEncoder

@login_required
def dashboard_view(request):
    user = request.user
    
    # 1. Fetch Data ONLY for the current user
    # Do NOT include partner data here as per request
    expenses = Expense.objects.filter(user=user).order_by('-date')
    incomes = Income.objects.filter(user=user).order_by('-date')
    
    # Accounts
    user_accounts = BankAccount.objects.filter(user=user)
    user_balance = user_accounts.aggregate(Sum('balance'))['balance__sum'] or 0

    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Chart Data Preparation (User Only)
    cat_data = {}
    for e in expenses:
        cat_name = e.category.name if e.category else 'Uncategorized'
        if cat_name not in cat_data:
            cat_data[cat_name] = 0
        cat_data[cat_name] += float(e.amount)
    
    pie_labels = list(cat_data.keys())
    pie_data = list(cat_data.values())

    welcome_name = user.first_name if user.first_name else user.username

    return render(request, 'dashboard/dashboard.html', {
        'welcome_name': welcome_name,
        'total_expenses': total_expenses,
        'total_income': total_income,
        'user_balance': user_balance,
        'user_accounts': user_accounts,
        # Chart Data
        'pie_labels': json.dumps(pie_labels),
        'pie_data': json.dumps(pie_data),
    })
