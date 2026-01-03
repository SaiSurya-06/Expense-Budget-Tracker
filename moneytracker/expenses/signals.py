from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Expense
from .services import check_and_notify_limit

@receiver(post_save, sender=Expense)
def check_budget_on_expense_save(sender, instance, created, **kwargs):
    """
    Trigger budget check whenever an expense is created or updated.
    """
    if instance.user:
        check_and_notify_limit(instance.user, instance)
