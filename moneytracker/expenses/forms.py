from django import forms
from .models import Expense, Income, BankAccount, Category

class ExpenseForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['account'].queryset = BankAccount.objects.filter(user=user)
        self.fields['account'].queryset = BankAccount.objects.filter(user=user)
        self.fields['category'].queryset = Category.objects.filter(user=user, type='expense')


    class Meta:
        model = Expense
        fields = ['amount', 'category', 'description', 'date', 'account']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'amount': forms.NumberInput(attrs={'placeholder': '0.00', 'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'description': forms.TextInput(attrs={'placeholder': 'What was this for?', 'class': 'form-input'}),
            'account': forms.Select(attrs={'class': 'form-input'}),
        }

class IncomeForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['account'].queryset = BankAccount.objects.filter(user=user)
        self.fields['category'].queryset = Category.objects.filter(user=user, type='income')

    class Meta:
        model = Income
        fields = ['amount', 'category', 'source', 'date', 'account']

        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'amount': forms.NumberInput(attrs={'placeholder': '0.00', 'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'source': forms.TextInput(attrs={'placeholder': 'Description (optional)', 'class': 'form-input'}),

            'account': forms.Select(attrs={'class': 'form-input'}),
        }

class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ['name', 'account_type', 'balance']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Chase Checking', 'class': 'form-input'}),
            'account_type': forms.Select(attrs={'class': 'form-input'}),
            'balance': forms.NumberInput(attrs={'placeholder': '0.00', 'class': 'form-input'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'type']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Groceries', 'class': 'form-input', 'required': True}),
            'type': forms.HiddenInput(),
        }

