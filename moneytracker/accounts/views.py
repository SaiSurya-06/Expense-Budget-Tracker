from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import InvitePartnerForm

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Profile created by signal
            # Log the user in
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def invite_partner(request):
    if request.method == 'POST':
        form = InvitePartnerForm(request.POST)
        if form.is_valid():
            partner_username = form.cleaned_data['username']
            partner_user = User.objects.get(username=partner_username)
            
            # Simple linking logic:
            # 1. Set current user's profile partner to partner_user
            # 2. Set partner_user's profile partner to current user
            
            # Link current user -> partner
            current_profile = request.user.profile
            current_profile.partner = partner_user
            current_profile.save()
            
            # Link partner -> current user
            # Ensure partner profile exists (it should via signals)
            partner_profile, _ = Profile.objects.get_or_create(user=partner_user)
            partner_profile.partner = request.user
            partner_profile.save()
            
            return redirect('dashboard')
    else:
        form = InvitePartnerForm()
    
    return render(request, 'accounts/invite_partner.html', {'form': form})
