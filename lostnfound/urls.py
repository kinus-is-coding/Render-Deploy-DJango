# project/urls.py (main urls file)

from django.contrib import admin
from django.urls import path, include
from users.views import CustomTokenObtainPairView # <-- Import your custom view
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),    
    
    # JWT Auth Endpoints (LOGIN)
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/users/', include('users.urls')),
    # Posts API Endpoints
    path('api/', include('feed.urls')), 
    
]