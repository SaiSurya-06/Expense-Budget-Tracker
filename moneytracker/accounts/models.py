from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    partner = models.OneToOneField(
        User,
        null=True,
        blank=True,
        related_name='partner_user',
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.user.username
