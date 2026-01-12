from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ExpenseForm, IncomeForm, BankAccountForm, CategoryForm, TransferForm
from .models import Expense, Income, BankAccount, Category, Transfer, Budget
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
        initial_data = {}
        if 'date' in request.GET:
            initial_data['date'] = request.GET.get('date')
        form = ExpenseForm(request.user, initial=initial_data)
    
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
        initial_data = {}
        if 'date' in request.GET:
            initial_data['date'] = request.GET.get('date')
        form = IncomeForm(request.user, initial=initial_data)
        
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
            # Check for duplicates before saving
            if Category.objects.filter(user=request.user, name__iexact=category.name, type=category_type).exists():
                form.add_error('name', f'A {category_type} category with this name already exists.')
            else:
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
def add_transfer(request):
    if request.method == 'POST':
        form = TransferForm(request.user, request.POST)
        if form.is_valid():
            transfer = form.save(commit=False)
            transfer.user = request.user
            
            # Update balances
            if transfer.from_account and transfer.to_account:
                transfer.from_account.balance -= transfer.amount
                transfer.to_account.balance += transfer.amount
                transfer.from_account.save()
                transfer.to_account.save()
            
            transfer.save()
            return redirect('transactions')
    else:
        form = TransferForm(request.user)
    
    return render(request, 'expenses/add_variable.html', {
        'form': form,
        'title': 'Is Self Transfer',
        'btn_text': 'Transfer',
        'type': 'primary'
    })

@login_required
def edit_transfer(request, pk):
    transfer = get_object_or_404(Transfer, pk=pk, user=request.user)
    old_from = transfer.from_account
    old_to = transfer.to_account
    old_amount = transfer.amount

    if request.method == 'POST':
        form = TransferForm(request.user, request.POST, instance=transfer)
        if form.is_valid():
            new_transfer = form.save(commit=False)
            
            # Revert old balances
            if old_from:
                old_from.balance += old_amount
                old_from.save()
            if old_to:
                old_to.balance -= old_amount
                old_to.save()
            
            # Apply new balances
            if new_transfer.from_account:
                new_transfer.from_account.balance -= new_transfer.amount
                new_transfer.from_account.save()
            if new_transfer.to_account:
                new_transfer.to_account.balance += new_transfer.amount
                new_transfer.to_account.save()
                
            new_transfer.save()
            return redirect('transactions')
    else:
        form = TransferForm(request.user, instance=transfer)
    
    return render(request, 'expenses/add_variable.html', {
        'form': form,
        'title': 'Edit Transfer',
        'btn_text': 'Update Transfer',
        'type': 'primary'
    })

@login_required
def delete_transfer(request, pk):
    transfer = get_object_or_404(Transfer, pk=pk, user=request.user)
    if request.method == 'POST':
        # Revert balances
        if transfer.from_account:
            transfer.from_account.balance += transfer.amount
            transfer.from_account.save()
        if transfer.to_account:
            transfer.to_account.balance -= transfer.amount
            transfer.to_account.save()
            
        transfer.delete()
        return redirect('transactions')
    
    return render(request, 'expenses/confirm_delete.html', {'object': transfer, 'type': 'Transfer'})


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


@login_required
def manage_categories(request):
    expenses_categories = Category.objects.filter(user=request.user, type='expense')
    income_categories = Category.objects.filter(user=request.user, type='income')
    return render(request, 'expenses/manage_categories.html', {
        'expenses_categories': expenses_categories,
        'income_categories': income_categories
    })

@login_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            # Check for duplicates (excluding current category)
            name = form.cleaned_data.get('name')
            if Category.objects.filter(user=request.user, name__iexact=name, type=category.type).exclude(pk=pk).exists():
                 form.add_error('name', f'A {category.type} category with this name already exists.')
            else:
                form.save()
                return redirect('manage_categories')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'expenses/add_variable.html', {
        'form': form,
        'title': f'Edit {category.type.title()} Category',
        'btn_text': 'Update Category',
        'type': 'primary'
    })

@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    
    # Check for usage
    linked_expenses = Expense.objects.filter(category=category).exists()
    linked_incomes = Income.objects.filter(category=category).exists()
    linked_budgets = Budget.objects.filter(category=category).exists()
    
    if linked_expenses or linked_incomes or linked_budgets:
        return render(request, 'expenses/delete_category_error.html', {
            'category': category,
            'linked_expenses': linked_expenses,
            'linked_incomes': linked_incomes,
            'linked_budgets': linked_budgets
        })

    if request.method == 'POST':
        category.delete()
        return redirect('manage_categories')
    
    return render(request, 'expenses/confirm_delete.html', {'object': category, 'type': 'Category'})


@login_required
def add_bulk_transactions(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            transactions_list = data.get('transactions', [])
            
            if not transactions_list:
                return JsonResponse({'success': False, 'error': 'No transactions provided'})

            saved_count = 0
            errors = []

            # Atomic block: All or nothing
            with transaction.atomic():
                # First pass: Validate all
                # To really do "atomic", we can just iterate and save. 
                # If any error, we raise an Exception or set_rollback inside the block.
                
                for index, item in enumerate(transactions_list):
                    t_type = item.get('type')
                    row_num = index + 1
                    
                    # Normalize data for Forms
                    form_data = {
                        'amount': item.get('amount'),
                        'date': item.get('date'),
                        'category': item.get('category_id'),
                        'account': item.get('account_id'),
                    }
                    
                    form = None
                    if t_type == 'expense':
                        form_data['description'] = item.get('description')
                        form = ExpenseForm(request.user, form_data)
                    elif t_type == 'income':
                        form_data['source'] = item.get('description') # Front-end sends 'description' for both
                        form = IncomeForm(request.user, form_data)
                    else:
                        errors.append(f"Row {row_num}: Invalid type '{t_type}'")
                        continue

                    if form.is_valid():
                        obj = form.save(commit=False)
                        obj.user = request.user
                        
                        # Handle Balance Update
                        if obj.account:
                            if t_type == 'expense':
                                obj.account.balance -= obj.amount
                            elif t_type == 'income':
                                obj.account.balance += obj.amount
                            obj.account.save()
                        
                        obj.save()
                        saved_count += 1
                    else:
                        # Format errors
                        field_errors = []
                        for field, err_list in form.errors.items():
                            field_errors.append(f"{field}: {err_list[0]}")
                        errors.append(f"Row {row_num}: " + ", ".join(field_errors))
                
                if errors:
                    # Rollback everything if there are errors
                    transaction.set_rollback(True)
                    return JsonResponse({'success': False, 'error': 'Validation Failed', 'details': errors})
            
            messages.success(request, f"Successfully added {saved_count} transactions.")
            return JsonResponse({'success': True, 'count': saved_count})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    else:
        # GET: Render the bulk add page
        categories_expense = Category.objects.filter(user=request.user, type='expense')
        categories_income = Category.objects.filter(user=request.user, type='income')
        accounts = BankAccount.objects.filter(user=request.user)
        
        # Serialize for JS
        # We need IDs and Names
        cat_exp_list = [{'id': c.id, 'name': c.name} for c in categories_expense]
        cat_inc_list = [{'id': c.id, 'name': c.name} for c in categories_income]
        acc_list = [{'id': a.id, 'name': a.name} for a in accounts]

        return render(request, 'expenses/add_bulk.html', {
            'categories_expense_json': json.dumps(cat_exp_list),
            'categories_income_json': json.dumps(cat_inc_list),
            'accounts_json': json.dumps(acc_list),
        })