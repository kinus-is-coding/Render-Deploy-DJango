from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action,api_view
from django.db import transaction 
from .models import Post,Locker
from .serializers import PostSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Q



class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]
    def get_queryset(self):
        queryset = Post.objects.filter(is_active=True)
        query = self.request.query_params.get('q', None)
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(location__icontains=query)
            ).distinct()
            
        return queryset

    def create(self, request, *args, **kwargs):
        # 1. Copy data và bóc tách locker_id
        data = request.data.copy()
        locker_id_str = data.get('locker') 
        
        try:
            locker_obj = Locker.objects.get(locker_id=locker_id_str)
        except Locker.DoesNotExist:
            return Response({"details": f"Tủ {locker_id_str} chưa tạo trong Admin!"}, status=400)

        
        # 3. Validate dữ liệu còn lại (title, location, questions...)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                author = request.user if request.user.is_authenticated else None               
                serializer.save(author=author, locker=locker_obj) 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"details": str(e)}, status=400)

    @action(detail=True, methods=['patch'], permission_classes=[permissions.AllowAny]) 
    def complete(self, request, pk=None):
        post = self.get_object()
        
        if not post.is_active:
            return Response({"error": "Bài đăng này đã hoàn tất hoặc không còn tồn tại!"}, status=400)

        try:
            with transaction.atomic():
                # 1. Tắt bài đăng trên Web
                post.is_active = False
                post.save()
                
                # 2. Xử lý cái tủ vật lý
                if post.locker:
                    locker = post.locker
                    # Bật công tắc để ESP32 mở khóa cho người mất lấy đồ
                    locker.trigger_unlock = True
                    locker.is_occupied = False
                    locker.save()
                    
                
            return Response({
                "status": "success", 
                "message": "Xác nhận thành công! Mời bạn lấy đồ tại tủ.",
                "locker_id": post.locker.locker_id if post.locker else None
            })
            
        except Exception as e:
            return Response({"error": "Lỗi hệ thống khi mở tủ", "details": str(e)}, status=500)
        







# 1. API cho ESP32 hóng lệnh (Chỉ đọc)
@api_view(['GET'])
@permission_classes([AllowAny])
def locker_status_api(request, locker_id):
    try:
        locker = Locker.objects.get(locker_id=locker_id)
        return Response({
            "unlock": locker.trigger_unlock,
            "is_occupied": locker.is_occupied
        })
    except Locker.DoesNotExist:
        return Response({"error": "Locker not found"}, status=404)

# 2. API cho ESP32 xác nhận đã xong (Để tắt trigger và báo có đồ hay chưa)
@api_view(['POST'])
@permission_classes([AllowAny])
def locker_confirm_action(request, locker_id):
    try:
        locker = Locker.objects.get(locker_id=locker_id)
        
        # ESP32 báo đã làm xong -> Tắt trigger ngay
        locker.trigger_unlock = False
        
        # Nếu ESP32 có cảm biến và gửi kèm {"has_item": true/false}
        has_item = request.data.get('has_item')
        if has_item is not None:
            locker.is_occupied = has_item
            
        locker.save()
        return Response({"status": "success", "message": "Trigger reset"})
    except Locker.DoesNotExist:
        return Response({"error": "Locker not found"}, status=404)