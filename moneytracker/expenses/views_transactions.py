from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Expense, Income, BankAccount, Category
from datetime import datetime
import csv
from django.http import HttpResponse
from django.core.paginator import Paginator

def get_transactions_for_user(user, account_id=None, category_id=None, transaction_type=None, search_query=None, start_date=None, end_date=None):
    # Base queries (using select_related to avoid N+1 queries)
    expense_qs = Expense.objects.filter(user=user).select_related('category', 'account').order_by('-date')
    income_qs = Income.objects.filter(user=user).select_related('category', 'account').order_by('-date')

    # Apply Filters
    if account_id:
        expense_qs = expense_qs.filter(account_id=account_id)
        income_qs = income_qs.filter(account_id=account_id)
    
    if category_id:
        expense_qs = expense_qs.filter(category_id=category_id)
        income_qs = income_qs.filter(category_id=category_id)
        
    if start_date:
        expense_qs = expense_qs.filter(date__gte=start_date)
        income_qs = income_qs.filter(date__gte=start_date)
        
    if end_date:
        expense_qs = expense_qs.filter(date__lte=end_date)
        income_qs = income_qs.filter(date__lte=end_date)

    if search_query:
        expense_qs = expense_qs.filter(description__icontains=search_query)
        income_qs = income_qs.filter(source__icontains=search_query)

    transactions = []

    # Process Expenses if type is not strictly 'income'
    if transaction_type != 'income':
        for e in expense_qs:
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

    # Process Income if type is not strictly 'expense'
    if transaction_type != 'expense':
        for i in income_qs:
            transactions.append({
                'id': i.id,
                'type': 'income',
                'date': i.date,
                'amount': i.amount,
                'category': i.category,
                'description': i.source if i.source else (i.category.name if i.category else 'Income'),
                'user': i.user,
                'account': i.account
            })
    
    transactions.sort(key=lambda x: x['date'], reverse=True)
    return transactions

@login_required
def transactions_view(request):
    # Extract Filter Params
    account_id = request.GET.get('account')
    category_id = request.GET.get('category')
    transaction_type = request.GET.get('type')
    search_query = request.GET.get('search')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    export_fmt = request.GET.get('export')

    # Fetch Transactions (FULL filtered list)
    transactions = get_transactions_for_user(
        request.user,
        account_id=account_id,
        category_id=category_id,
        transaction_type=transaction_type,
        search_query=search_query,
        start_date=start_date,
        end_date=end_date
    )

    # 1️⃣ CSV Export
    if export_fmt == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            f'attachment; filename="transactions_{datetime.now().strftime("%Y%m%d")}.csv"'
        )

        writer = csv.writer(response)
        writer.writerow(['Date', 'Type', 'Description', 'Category', 'Account', 'Amount'])

        for t in transactions:
            writer.writerow([
                t['date'],
                t['type'].title(),
                t['description'],
                t['category'].name if t['category'] else '—',
                t['account'].name if t['account'] else '—',
                t['amount'],
            ])
        return response

    # 2️⃣ Totals
    total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
    total_expense = sum(t['amount'] for t in transactions if t['type'] == 'expense')
    net_total = total_income - total_expense

    # 3️⃣ Pagination
    paginator = Paginator(transactions, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # 4️⃣ Dropdown data
    user_accounts = BankAccount.objects.filter(user=request.user)
    user_categories = Category.objects.filter(user=request.user)

    profile = getattr(request.user, 'profile', None)
    has_partner = profile.partner is not None if profile else False

    # 5️⃣ Query string (without page)
    params = request.GET.copy()
    params.pop('page', None)
    query_string = params.urlencode()

    # ✅ DEFINE CONTEXT ONCE
    context = {
        # Pagination
        'transactions': page_obj,   # TEMPLATE USES THIS
        'page_obj': page_obj,       # (optional but safe)
        'query_string': query_string,

        # UI
        'view_type': 'me',
        'has_partner': has_partner,
        'accounts': user_accounts,
        'categories': user_categories,

        # Totals
        'filtered_total_income': total_income,
        'filtered_total_expense': total_expense,
        'filtered_net_total': net_total,

        # Persist filters
        'selected_account': int(account_id) if account_id else None,
        'selected_category': int(category_id) if category_id else None,
        'selected_type': transaction_type,
        'search_query': search_query,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'expenses/transactions.html', context)

@login_required
def partner_transactions_view(request):
    profile = getattr(request.user, 'profile', None)
    partner = profile.partner if profile else None
    
    if not partner:
        return redirect('transactions')

    # Reuse generic fetching logic? 
    # Partner view might not need all filters yet, but let's support them if easy.
    # For now, keep it simple as originally requested, or user asked for "Transactions page".
    # Assuming user meant their own transactions page primarily.
    
    transactions = get_transactions_for_user(partner)
    
    accounts = BankAccount.objects.filter(user=partner)

    return render(request, 'expenses/transactions.html', {
        'transactions': transactions,
        'view_type': 'partner',
        'partner': partner,
        'accounts': accounts
    })
