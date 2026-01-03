from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from .models import Connection

@login_required
def shared_view(request):
    """
    Main view for the Shared Hub.
    Displays active connections and pending requests.
    """
    user = request.user
    
    # Active Connections (Where user is sender OR receiver, and status is accepted)
    active_connections_qs = Connection.objects.filter(
        (Q(sender=user) | Q(receiver=user)),
        status='accepted'
    )
    
    partners = []
    for conn in active_connections_qs:
        if conn.sender == user:
            partners.append(conn.receiver)
        else:
            partners.append(conn.sender)
            
    # Pending Incoming Requests (Where user is receiver)
    pending_requests = Connection.objects.filter(
        receiver=user,
        status='pending'
    )
    
    # Pending Sent Requests (Where user is sender)
    sent_requests = Connection.objects.filter(
        sender=user,
        status='pending'
    )
    
    return render(request, 'dashboard/shared_profile.html', {
        'partners': partners,
        'pending_requests': pending_requests,
        'sent_requests': sent_requests
    })

@login_required
def send_request(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            receiver = User.objects.get(username=username)
            
            if receiver == request.user:
                messages.error(request, "You cannot invite yourself.")
                return redirect('shared_view')
                
            # Check if connection already exists
            existing = Connection.objects.filter(
                (Q(sender=request.user) & Q(receiver=receiver)) |
                (Q(sender=receiver) & Q(receiver=request.user))
            ).first()
            
            if existing:
                if existing.status == 'accepted':
                    messages.info(request, "You are already connected.")
                elif existing.status == 'pending':
                    messages.info(request, "A request is already pending.")
                else:
                    # If rejected, maybe allow re-sending? For now just say request exists.
                    messages.info(request, "Request status: " + existing.status)
            else:
                Connection.objects.create(sender=request.user, receiver=receiver)
                messages.success(request, f"Invitation sent to {receiver.username}!")
                
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            
    return redirect('shared_view')

@login_required
def respond_request(request, request_id, action):
    conn = get_object_or_404(Connection, id=request_id, receiver=request.user)
    
    if action == 'accept':
        conn.status = 'accepted'
        conn.save()
        messages.success(request, f"You are now connected with {conn.sender.username}!")
    elif action == 'reject':
        conn.status = 'rejected'
        conn.save()
        messages.info(request, "Request rejected.")
    elif action == 'cancel':
         # Allow deleting/disconnecting?
         pass
         
    return redirect('shared_view')

@login_required
def disconnect_user(request, user_id):
    # Remove connection with specific user
    other_user = get_object_or_404(User, id=user_id)
    Connection.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).delete()
    messages.success(request, "Connection removed.")
    return redirect('shared_view')
