# users/urls.py
from django.urls import path
from .views import UserRegistrationView

urlpatterns = [
    # The full URL for registration will be /api/users/register/
    path('register/', UserRegistrationView.as_view(), name='user_register'), 
]