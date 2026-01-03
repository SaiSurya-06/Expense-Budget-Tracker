from django.db import models
from django.contrib.auth.models import User

# Standard types for reference, but we will allow dynamic creation via a proper model if needed, 
# or just keep these for the 'type' of account while the user defines the 'name'.
ACCOUNT_TYPES = [
    ('checking', 'Checking'),
    ('savings', 'Savings'),
    ('credit', 'Credit Card'),
    ('cash', 'Cash'),
    ('investment', 'Investment'),
    ('other', 'Other'),
]

class Category(models.Model):
    CATEGORY_TYPES = [
        ('expense', 'Expense'),
        ('income', 'Income'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=10, choices=CATEGORY_TYPES, default='expense')
    
    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class BankAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    # We keep account_type as a high-level grouping, but users define the specific "Account Name"
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='checking')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"

class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(BankAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name='incomes')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    source = models.CharField(max_length=100, blank=True) # Making source optional as category can replace it
    date = models.DateField()

    def __str__(self):
        return f"{self.user.username} - {self.amount}"


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(BankAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # Changed from hardcoded choices to ForeignKey
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True) 
    description = models.CharField(max_length=255)
    date = models.DateField()

    def __str__(self):
        return f"{self.user.username} - {self.amount}"

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    limit_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'month', 'category')
        ordering = ['-month', 'category__name']

    def __str__(self):
        cat = self.category.name if self.category else "Total"
        return f"{self.user.username} - {self.month} - {cat}"

class BudgetNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='notifications')
    sent_at = models.DateTimeField(auto_now_add=True)
    exceeded_amount = models.DecimalField(max_digits=12, decimal_places=2)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Notification for {self.budget.id}"
