from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='satta_dashboard'),
    path('magic/', views.api_magic_numbers, name='api_magic_numbers'),
]
