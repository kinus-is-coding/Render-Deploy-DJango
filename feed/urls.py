# feed/urls.py
from django.urls import path
from .views import PostViewSet # Chỉ cần import PostViewSet thôi vì nó lo hết rồi

urlpatterns = [
  
    path('posts/', PostViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='post-list-create'),

  
    path('posts/<int:pk>/complete/', PostViewSet.as_view({
        'patch': 'complete'
    }), name='post-complete'),

    path('posts/<int:pk>/', PostViewSet.as_view({
        'get': 'retrieve', 
        'put': 'update', 
        'patch': 'partial_update', 
        'delete': 'destroy'
    }), name='post-detail'),
]