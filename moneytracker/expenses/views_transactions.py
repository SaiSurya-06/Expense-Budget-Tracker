from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Expense, Income, BankAccount

def get_transactions_for_user(user):
    expenses = Expense.objects.filter(user=user).order_by('-date')
    incomes = Income.objects.filter(user=user).order_by('-date')
    
    transactions = []
    for e in expenses:
        transactions.append({
            'id': e.id,
            'type': 'expense',
            'date': e.date,
            'amount': e.amount,
            'category': e.category,
            'description': e.description,
            'user': e.user,
            'account': e.account
        })
    for i in incomes:
        transactions.append({
            'id': i.id,
            'type': 'income',
            'date': i.date,
            'amount': i.amount,
            
            'category': i.category or i.source,
            'description': i.source if i.category else 'Income',
            'user': i.user,
            'account': i.account
        })

    
    transactions.sort(key=lambda x: x['date'], reverse=True)
    return transactions

@login_required
def transactions_view(request):
    # Show ONLY current user transactions
    transactions = get_transactions_for_user(request.user)
    
    profile = getattr(request.user, 'profile', None)
    has_partner = profile.partner is not None if profile else False

    return render(request, 'expenses/transactions.html', {
        'transactions': transactions,
        'view_type': 'me',
        'has_partner': has_partner
    })

@login_required
def partner_transactions_view(request):
    profile = getattr(request.user, 'profile', None)
    partner = profile.partner if profile else None
    
    if not partner:
        return redirect('transactions')

    # Show ONLY partner transactions
    transactions = get_transactions_for_user(partner)
    
    # Also fetch partner's accounts for the "account balances" requirement
    accounts = BankAccount.objects.filter(user=partner)

    return render(request, 'expenses/transactions.html', {
        'transactions': transactions,
        'view_type': 'partner',
        'partner': partner,
        'accounts': accounts
    })
