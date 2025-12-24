from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ExpenseForm, IncomeForm, BankAccountForm, CategoryForm
from .models import Expense, Income, BankAccount, Category
from django.http import JsonResponse
import json

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.user, request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            
            # Update account balance
            if expense.account:
                expense.account.balance -= expense.amount
                expense.account.save()
                
            expense.save()
            
            next_url = request.POST.get('next')
            if next_url == 'transactions':
                return redirect('transactions')
            return redirect('dashboard')
    else:
        form = ExpenseForm(request.user)
    
    return render(request, 'expenses/add_variable.html', {
        'form': form,
        'title': 'Add Expense',
        'btn_text': 'Spend',
        'type': 'expense',
        'next': request.GET.get('next', '')
    })


@login_required
def add_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.user, request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            
            # Update account balance
            if income.account:
                income.account.balance += income.amount
                income.account.save()
                
            income.save()
            
            next_url = request.POST.get('next')
            if next_url == 'transactions':
                return redirect('transactions')
            return redirect('dashboard')
    else:
        form = IncomeForm(request.user)
        
    return render(request, 'expenses/add_variable.html', {
        'form': form,
        'title': 'Add Income',
        'btn_text': 'Earn',
        'type': 'income',
        'next': request.GET.get('next', '')
    })


@login_required
def add_account(request):
    if request.method == 'POST':
        form = BankAccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user
            account.save()
            return redirect('dashboard')
    else:
        form = BankAccountForm()
    
    return render(request, 'expenses/add_variable.html', {
        'form': form,
        'title': 'Add Bank Account',
        'btn_text': 'Add Account',
        'type': 'primary' 
    })

@login_required
def add_category(request):
    # Determine type from GET parameter, default to expense
    category_type = request.GET.get('type', 'expense')
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            # form should include type as hidden input, or we set it here if missing
            if not category.type:
                 category.type = category_type
            category.save()
            return redirect('add_expense') # Default redirect
    else:
        form = CategoryForm(initial={'type': category_type})
    
    return render(request, 'expenses/add_variable.html', {
        'form': form,
        'title': f'Create New {category_type.title()} Category',
        'btn_text': 'Create',
        'type': 'primary'
    })


# --- CRUD Operations ---

@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    old_account = expense.account
    old_amount = expense.amount

    if request.method == 'POST':
        form = ExpenseForm(request.user, request.POST, instance=expense)
        if form.is_valid():
            new_expense = form.save(commit=False)
            
            # Revert old balance
            if old_account:
                old_account.balance += old_amount
                old_account.save()
            
            # Apply new balance
            if new_expense.account:
                new_expense.account.balance -= new_expense.amount
                new_expense.account.save()
                
            new_expense.save()
            return redirect('transactions')
    else:
        form = ExpenseForm(request.user, instance=expense)
    
    return render(request, 'expenses/add_variable.html', {
        'form': form,
        'title': 'Edit Expense',
        'btn_text': 'Update',
        'type': 'expense'
    })

@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        # Revert balance
        if expense.account:
            expense.account.balance += expense.amount
            expense.account.save()
        expense.delete()
        return redirect('transactions')
    
    return render(request, 'expenses/confirm_delete.html', {'object': expense, 'type': 'Expense'})

@login_required
def edit_income(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    old_account = income.account
    old_amount = income.amount

    if request.method == 'POST':
        form = IncomeForm(request.user, request.POST, instance=income)
        if form.is_valid():
            new_income = form.save(commit=False)
            
            # Revert old balance
            if old_account:
                old_account.balance -= old_amount
                old_account.save()
            
            # Apply new balance
            if new_income.account:
                new_income.account.balance += new_income.amount
                new_income.account.save()
                
            new_income.save()
            return redirect('transactions')
    else:
        form = IncomeForm(request.user, instance=income)
    
    return render(request, 'expenses/add_variable.html', {
        'form': form,
        'title': 'Edit Income',
        'btn_text': 'Update',
        'type': 'income'
    })

@login_required
def delete_income(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        # Revert balance
        if income.account:
            income.account.balance -= income.amount
            income.account.save()
        income.delete()
        return redirect('transactions')
    
    return render(request, 'expenses/confirm_delete.html', {'object': income, 'type': 'Income'})

@login_required
def manage_accounts(request):
    accounts = BankAccount.objects.filter(user=request.user)
    return render(request, 'expenses/manage_accounts.html', {'accounts': accounts})

@login_required
def edit_account(request, pk):
    account = get_object_or_404(BankAccount, pk=pk, user=request.user)
    if request.method == 'POST':
        form = BankAccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            return redirect('manage_accounts')
    else:
        form = BankAccountForm(instance=account)
    
    return render(request, 'expenses/add_variable.html', {
        'form': form,
        'title': 'Edit Bank Account',
        'btn_text': 'Update Account',
        'type': 'primary'
    })

@login_required
def delete_account(request, pk):
    account = get_object_or_404(BankAccount, pk=pk, user=request.user)
    
    # Check for linked transactions
    linked_expenses = Expense.objects.filter(account=account).exists()
    linked_incomes = Income.objects.filter(account=account).exists()
    
    if linked_expenses or linked_incomes:
        # Prevent deletion
        return render(request, 'expenses/delete_account_error.html', {
            'account': account,
            'linked_expenses': linked_expenses,
            'linked_incomes': linked_incomes
        })

    if request.method == 'POST':
        account.delete()
        return redirect('manage_accounts')
    
    return render(request, 'expenses/confirm_delete.html', {'object': account, 'type': 'Bank Account'})

@login_required
def api_create_category(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            cat_type = data.get('type', 'expense') # Default to expense if not provided
            
            if not name:
                return JsonResponse({'success': False, 'error': 'Name is required'})
            
            # Check if exists
            if Category.objects.filter(user=request.user, name__iexact=name, type=cat_type).exists():
                 return JsonResponse({'success': False, 'error': 'Category already exists'})

            category = Category.objects.create(user=request.user, name=name, type=cat_type)
            return JsonResponse({'success': True, 'id': category.id, 'name': category.name})
        except Exception as e:
             return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid method'})


