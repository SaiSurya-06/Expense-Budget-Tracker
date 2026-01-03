# views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from expenses.models import Expense, Income, Budget, BankAccount
from django.db.models import Sum, Q
from datetime import datetime
import json
from django.core.serializers.json import DjangoJSONEncoder
from calendar import month_name

@login_required
def dashboard_view(request):
    user = request.user

    # ✅ Month / Year from query params (fallback = current)
    selected_month = int(request.GET.get('month', datetime.now().month))
    selected_year = int(request.GET.get('year', datetime.now().year))

    # =============================
    # Expenses (selected month/year)
    # =============================
    expenses = Expense.objects.filter(
        user=user,
        date__month=selected_month,
        date__year=selected_year
    ).order_by('-date')

    # =============================
    # Income (selected month/year)
    # =============================
    incomes = Income.objects.filter(
        user=user,
        date__month=selected_month,
        date__year=selected_year
    ).order_by('-date')

    # =============================
    # Accounts
    # =============================
    user_accounts = BankAccount.objects.filter(user=user)

    # ✅ Net Worth (EXCLUDE credit cards)
    net_worth = BankAccount.objects.filter(
        user=user
    ).exclude(
        account_type='credit'
    ).aggregate(
        total=Sum('balance')
    )['total'] or 0

    # =============================
    # Monthly totals
    # =============================
    total_expenses = expenses.aggregate(
        total=Sum('amount')
    )['total'] or 0

    total_income = incomes.aggregate(
        total=Sum('amount')
    )['total'] or 0

    # Net cash flow
    net_cash_flow = float(total_income) - float(total_expenses)

    # =============================
    # Pie Chart Data (Expenses)
    # =============================
    cat_data = {}
    for e in expenses:
        cat_name = e.category.name if e.category else 'Uncategorized'
        cat_data[cat_name] = cat_data.get(cat_name, 0) + float(e.amount)

    pie_labels = list(cat_data.keys())
    pie_data = list(cat_data.values())

    # Welcome name
    welcome_name = user.first_name or user.username

    return render(request, 'dashboard/dashboard.html', {
        'welcome_name': welcome_name,

        # Numbers
        'total_expenses': total_expenses,
        'total_income': total_income,
        'net_cash_flow': net_cash_flow,
        'user_balance': net_worth,  # ✅ Net worth excluding credit cards
        'user_accounts': user_accounts,

        # Charts
        'pie_labels': json.dumps(pie_labels),
        'pie_data': json.dumps(pie_data),

        # ✅ Needed for UI dropdowns
        'selected_month': selected_month,
        'selected_year': selected_year,

        'months': [
            {'value': i, 'label': month_name[i]}
            for i in range(1, 13)
        ],

        'years': [
            {'value': y, 'label': y}
            for y in range(datetime.now().year, datetime.now().year - 10, -1)
        ],
    })


# Add this new view for real-time data updates
@login_required
def dashboard_live_data(request):
    """
    API endpoint for AJAX-based dashboard updates
    Supports month & year filtering for cash flow and charts
    """

    user = request.user

    # ✅ Month & Year from query params (fallback = current)
    month = int(request.GET.get('month', datetime.now().month))
    year = int(request.GET.get('year', datetime.now().year))

    # =============================
    # Expenses & Income (Filtered)
    # =============================
    expenses = Expense.objects.filter(
        user=user,
        date__month=month,
        date__year=year
    )

    incomes = Income.objects.filter(
        user=user,
        date__month=month,
        date__year=year
    )

    # =============================
    # Monthly totals
    # =============================
    total_expenses = expenses.aggregate(
        total=Sum('amount')
    )['total'] or 0

    total_income = incomes.aggregate(
        total=Sum('amount')
    )['total'] or 0

    net_cash_flow = float(total_income) - float(total_expenses)

    # =============================
    # Net Worth (GLOBAL – exclude credit cards)
    # =============================
    net_worth = BankAccount.objects.filter(
        user=user
    ).exclude(
        account_type='credit'
    ).aggregate(
        total=Sum('balance')
    )['total'] or 0

    # =============================
    # Pie Chart Data (Expenses)
    # =============================
    cat_data = {}
    for e in expenses:
        cat_name = e.category.name if e.category else 'Uncategorized'
        cat_data[cat_name] = cat_data.get(cat_name, 0) + float(e.amount)

    # =============================
    # Response
    # =============================
    return JsonResponse({
        'month': month,
        'year': year,

        'net_worth': float(net_worth),
        'total_income': float(total_income),
        'total_expenses': float(total_expenses),
        'net_cash_flow': float(net_cash_flow),

        'pie_labels': list(cat_data.keys()),
        'pie_data': list(cat_data.values()),

        'timestamp': datetime.now().isoformat(),
    })