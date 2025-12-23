from django import forms
from django.contrib.auth.models import User

class InvitePartnerForm(forms.Form):
    username = forms.CharField(max_length=150, help_text="Enter your partner's username to link accounts.")
    
    def clean_username(self):
        username = self.cleaned_data['username']
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError("User with this username does not exist.")
        return username
