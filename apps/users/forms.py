from django.contrib.auth.forms import UserCreationForm
from apps.users.models import User
from django import forms

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("phone", "name")
