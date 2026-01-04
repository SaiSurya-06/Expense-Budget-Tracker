from django import forms
from .models import Expense, Income, BankAccount, Category, Transfer

class ExpenseForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

class TransferForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['from_account'].queryset = BankAccount.objects.filter(user=user)
        self.fields['to_account'].queryset = BankAccount.objects.filter(user=user)

    def clean(self):
        cleaned_data = super().clean()
        from_account = cleaned_data.get('from_account')
        to_account = cleaned_data.get('to_account')

        if from_account and to_account and from_account == to_account:
            raise forms.ValidationError("Source and destination accounts cannot be the same.")
        return cleaned_data

    class Meta:
        model = Transfer
        fields = ['amount', 'from_account', 'to_account', 'description', 'date']
        widgets = {
             'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
             'amount': forms.NumberInput(attrs={'placeholder': '0.00', 'class': 'form-input'}),
             'from_account': forms.Select(attrs={'class': 'form-input'}),
             'to_account': forms.Select(attrs={'class': 'form-input'}),
             'description': forms.TextInput(attrs={'placeholder': 'Transfer details...', 'class': 'form-input'}),
        }
