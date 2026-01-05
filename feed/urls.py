# feed/urls.py
from django.urls import path
from .views import PostViewSet,locker_status_api,locker_confirm_action 

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
    path('locker/<str:locker_id>/status/',locker_status_api),
    path('locker/<str:locker_id>/confirm/', locker_confirm_action),
]