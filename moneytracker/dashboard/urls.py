# dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('live-data/', views.dashboard_live_data, name='dashboard_live_data'),
]