from django import forms
from .models import Budget, Category
from datetime import date

class BudgetGlobalForm(forms.ModelForm):
    month = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'month', 'class': 'form-control'}),
        label="Budget Month",
        input_formats=['%Y-%m', '%Y-%m-%d']
    )
    limit_amount = forms.DecimalField(
        max_digits=12, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'})
    )

    class Meta:
        model = Budget
        fields = ['month', 'limit_amount']

    def clean_month(self):
        month = self.cleaned_data['month']
        # Normalize to first of month
        return date(month.year, month.month, 1)

class BudgetCategoryForm(forms.Form):
    """
    Dynamic form to handle multiple categories.
    We won't use a ModelForm directly because we want to iterate over ALL categories 
    and show inputs for them, pre-filling existing limits.
    """
    pass 
