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
import calendar

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

    # =============================
    # Calendar Data Logic
    # =============================
    cal = calendar.Calendar(firstweekday=6)  # 0=Monday, 6=Sunday
    month_days_matrix = cal.monthdayscalendar(selected_year, selected_month)

    daily_stats = {}

    for inc in incomes:
        day = inc.date.day
        if day not in daily_stats:
            daily_stats[day] = {'income': 0, 'expense': 0, 'count': 0}
        daily_stats[day]['income'] += float(inc.amount)
        daily_stats[day]['count'] += 1

    for exp in expenses:
        day = exp.date.day
        if day not in daily_stats:
            daily_stats[day] = {'income': 0, 'expense': 0, 'count': 0}
        daily_stats[day]['expense'] += float(exp.amount)
        daily_stats[day]['count'] += 1

    calendar_weeks = []
    for week in month_days_matrix:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append(None)
            else:
                stats = daily_stats.get(day, {'income': 0, 'expense': 0})
                income = stats['income']
                expense = stats['expense']
                total = income - expense
                week_data.append({
                    'day': day,
                    'income': income,
                    'expense': expense,
                    'total': total,
                    'has_data': income > 0 or expense > 0
                })
        calendar_weeks.append(week_data)

    # ✅ Daily Transactions Data for Popup (Grouped by Day)
    daily_details = {}
    
    # Process Incomes
    for inc in incomes:
        day = inc.date.day
        if day not in daily_details:
             daily_details[day] = []
        daily_details[day].append({
            'type': 'income',
            'description': inc.source or inc.category.name if inc.category else 'Income',
            'amount': float(inc.amount),
            'category': inc.category.name if inc.category else 'Uncategorized',
            'icon': getattr(inc.category, 'icon', 'fa-money-bill-wave') if inc.category else 'fa-money-bill-wave',
            'account': inc.account.name if inc.account else 'Cash'
        })

    # Process Expenses
    for exp in expenses:
        day = exp.date.day
        if day not in daily_details:
             daily_details[day] = []
        daily_details[day].append({
            'type': 'expense',
            'description': exp.description,
            'amount': float(exp.amount),
            'category': exp.category.name if exp.category else 'Uncategorized',
            'icon': getattr(exp.category, 'icon', 'fa-shopping-cart') if exp.category else 'fa-shopping-cart', # Assuming category has icon field or fallback
            'account': exp.account.name if exp.account else 'Cash'
        })
    
    # Sort transactions within each day (optional, could sort by ID or keep as is) (Actually models are ordered by -date, but here we just append)
    
    # Serialize for template
    daily_transactions_json = json.dumps(daily_details)

    # ✅ Month Navigation Logic
    if selected_month == 1:
        prev_month = 12
        prev_year = selected_year - 1
    else:
        prev_month = selected_month - 1
        prev_year = selected_year

    if selected_month == 12:
        next_month = 1
        next_year = selected_year + 1
    else:
        next_month = selected_month + 1
        next_year = selected_year

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

        # Calendar
        'calendar_weeks': calendar_weeks,
        'daily_transactions_json': daily_transactions_json,

        # ✅ Needed for UI dropdowns
        'selected_month': selected_month,
        'selected_year': selected_year,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,

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