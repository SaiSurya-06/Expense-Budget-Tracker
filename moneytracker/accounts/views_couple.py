from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Profile

@login_required
def couple_view(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    partner = profile.partner if profile else None
    
    return render(request, 'dashboard/couple.html', {
        'partner': partner
    })
