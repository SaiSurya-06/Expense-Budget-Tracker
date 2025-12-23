from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ExpenseForm, IncomeForm, BankAccountForm, CategoryForm
from .models import Expense, Income, BankAccount, Category

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
            return redirect('dashboard')
    else:
        form = ExpenseForm(request.user)
    
    return render(request, 'expenses/add_variable.html', {
        'form': form,
        'title': 'Add Expense',
        'btn_text': 'Spend',
        'type': 'expense'
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
            return redirect('dashboard')
    else:
        form = IncomeForm(request.user)
        
    return render(request, 'expenses/add_variable.html', {
        'form': form,
        'title': 'Add Income',
        'btn_text': 'Earn',
        'type': 'income'
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
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            return redirect('add_expense') # Redirect to add expense so they can use it immediately works well
    else:
        form = CategoryForm()
    
    return render(request, 'expenses/add_variable.html', {
        'form': form,
        'title': 'Create New Category',
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
