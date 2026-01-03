from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Budget, Category
from .forms_budget import BudgetGlobalForm
from .services import get_budget_dashboard_data, check_budget_state
from datetime import date, datetime

@login_required
def budget_list(request):
    """
    Lists all monthly budgets with summary statistics.
    """
    budgets_qs = Budget.objects.filter(user=request.user).order_by('-month')
    months = sorted(list(set(b.month for b in budgets_qs)), reverse=True)
    
    budget_summaries = []
    for m in months:
        data = get_budget_dashboard_data(request.user, m)
        budget_summaries.append(data)
        
    return render(request, 'expenses/budget_list.html', {'budgets': budget_summaries})

@login_required
def budget_manage(request, month_str=None):
    """
    Create or Edit a budget for a specific month.
    """
    user = request.user
    category_limits = {} 
    
    initial_month = None
    if month_str:
        try:
            initial_month = datetime.strptime(month_str, '%Y-%m').date()
        except ValueError:
            pass
            
    if request.method == 'POST':
        form = BudgetGlobalForm(request.POST)
        if form.is_valid():
            month = form.cleaned_data['month']
            limit_amount = form.cleaned_data['limit_amount']
            
            # 1. Save Global Budget
            global_budget, _ = Budget.objects.update_or_create(
                user=user,
                month=month,
                category=None,
                defaults={'limit_amount': limit_amount}
            )
            check_budget_state(user, global_budget)
            
            # 2. Save Category Budgets
            categories = Category.objects.filter(user=user)
            for cat in categories:
                val = request.POST.get(f'cat_limit_{cat.id}')
                if val:
                    try:
                        val_decimal = float(val)
                        if val_decimal > 0:
                            cat_budget, _ = Budget.objects.update_or_create(
                                user=user,
                                month=month,
                                category=cat,
                                defaults={'limit_amount': val_decimal}
                            )
                            check_budget_state(user, cat_budget)
                        else:
                             # 0 means remove
                            deleted_count, _ = Budget.objects.filter(user=user, month=month, category=cat).delete()
                    except ValueError:
                         pass 
                else:
                    # Empty means remove
                    Budget.objects.filter(user=user, month=month, category=cat).delete()
            
            messages.success(request, f"Budget for {month.strftime('%B %Y')} updated!")
            return redirect('budget_list')
        else:
            # Form invalid, preserve category inputs if possible
            for key, value in request.POST.items():
                if key.startswith('cat_limit_'):
                    try:
                        cat_id = int(key.replace('cat_limit_', ''))
                        category_limits[cat_id] = value
                    except ValueError:
                        pass
    
    else:
        # GET
        initial_data = {}
        
        if initial_month:
            # Pre-fill
            try:
                global_b = Budget.objects.get(user=user, month=initial_month, category__isnull=True)
                initial_data = {'month': initial_month, 'limit_amount': global_b.limit_amount}
            except Budget.DoesNotExist:
                initial_data = {'month': initial_month}
                
            # Get existing category budgets
            cat_budgets = Budget.objects.filter(user=user, month=initial_month, category__isnull=False)
            for cb in cat_budgets:
                category_limits[cb.category_id] = cb.limit_amount
                
        form = BudgetGlobalForm(initial=initial_data)
        
    # Get all categories to display inputs
    categories = Category.objects.filter(user=user)
    cat_form_data = []
    
    for cat in categories:
        cat_form_data.append({
            'category': cat,
            'limit': category_limits.get(cat.id, '')
        })
        
    return render(request, 'expenses/budget_manage.html', {
        'form': form,
        'cat_form_data': cat_form_data,
        'month_str': month_str,
        'is_edit': month_str is not None
    })
    
@login_required
def budget_delete(request, month_str):
    if request.method == 'POST':
        try:
            month = datetime.strptime(month_str, '%Y-%m').date()
            Budget.objects.filter(user=request.user, month=month).delete()
            # Also cleanup notifications? Cascade should handle it if related_name is correct (it is).
            messages.success(request, "Budget deleted.")
        except ValueError:
            messages.error(request, "Invalid date.")
            
    return redirect('budget_list')
