from django.db.models import Sum
from .models import Expense, Budget, BudgetNotification
from django.utils import timezone
from datetime import date
from decimal import Decimal

def get_month_range(date_obj):
    """Return the first and last day of the month for a given date."""
    year = date_obj.year
    month = date_obj.month
    
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)
    return start_date, end_date

def calculate_spending(user, month_date, category=None):
    """
    Calculates spending for a user in a given month.
    If category is provided, filters by that category.
    """
    start_date, next_month_start = get_month_range(month_date)
    
    qs = Expense.objects.filter(
        user=user,
        date__gte=start_date,
        date__lt=next_month_start
    )
    
    if category:
        qs = qs.filter(category=category)
        
    val = qs.aggregate(Sum('amount'))['amount__sum']
    return Decimal(val) if val is not None else Decimal('0.00')

def check_budget_state(user, budget):
    """
    Checks a specific budget to see if it is exceeded.
    Manages notification state (activate/deactivate).
    """
    spent = calculate_spending(user, budget.month, category=budget.category)
    
    if spent > budget.limit_amount:
        # Exceeded
        _create_notification_if_needed(user, budget, spent)
    else:
        # Within limits - reset notification state
        _reset_notification(user, budget)

def check_and_notify_limit(user, expense):
    """
    Checks if the given expense causes a budget breach.
    Identifies relevant budgets (Category & Global) and checks them.
    """
    expense_date = expense.date
    month_start = date(expense_date.year, expense_date.month, 1)
    
    # 1. Check Category Limit
    if expense.category:
        try:
            cat_budget = Budget.objects.get(user=user, month=month_start, category=expense.category)
            check_budget_state(user, cat_budget)
        except Budget.DoesNotExist:
            pass 

    # 2. Check Global Limit
    try:
        global_budget = Budget.objects.get(user=user, month=month_start, category__isnull=True)
        check_budget_state(user, global_budget)
    except Budget.DoesNotExist:
        pass 

def _create_notification_if_needed(user, budget, current_spent):
    """
    Internal helper to create budget notification if rate limits allow.
    """
    # Check for ACTIVE notification
    last_notif = BudgetNotification.objects.filter(budget=budget, active=True).first()
    
    if last_notif:
        # Already active, don't spam.
        return

    # No active notification, so create one.
    BudgetNotification.objects.create(
        user=user,
        budget=budget,
        exceeded_amount=current_spent - budget.limit_amount,
        active=True
    )

def _reset_notification(user, budget):
    """
    If the budget is no longer exceeded, mark notifications as inactive.
    """
    BudgetNotification.objects.filter(budget=budget, active=True).update(active=False)

def get_budget_dashboard_data(user, month_date):
    """
    Returns a structured object with budget vs spending data for the UI.
    """
    start_date = date(month_date.year, month_date.month, 1)
    
    # Get all budgets for this month
    budgets = Budget.objects.filter(user=user, month=start_date)
    
    global_budget = None
    category_budgets = []
    
    for b in budgets:
        if b.category is None:
            global_budget = b
        else:
            category_budgets.append(b)
            
    # Calculate global spending
    total_spent = calculate_spending(user, start_date)
    
    global_data = None
    if global_budget:
        global_data = {
            'limit': global_budget.limit_amount,
            'spent': total_spent,
            'remaining': global_budget.limit_amount - total_spent,
            'percent': (total_spent / global_budget.limit_amount) * 100 if global_budget.limit_amount > 0 else 100,
            'is_exceeded': total_spent > global_budget.limit_amount,
            'obj': global_budget
        }
        
    cat_data = []
    for cb in category_budgets:
        c_spent = calculate_spending(user, start_date, category=cb.category)
        cat_data.append({
            'category': cb.category,
            'limit': cb.limit_amount,
            'spent': c_spent,
            'remaining': cb.limit_amount - c_spent,
            'percent': (c_spent / cb.limit_amount) * 100 if cb.limit_amount > 0 else 100,
            'is_exceeded': c_spent > cb.limit_amount,
            'obj': cb
        })
        
    return {
        'month': start_date,
        'global': global_data,
        'categories': cat_data,
        'total_spent': total_spent
    }
