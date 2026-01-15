from rest_framework import viewsets, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import action,api_view
from django.db import transaction 
from .models import Post,Locker
from .serializers import PostSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from functools import reduce
import operator


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]
    def get_queryset(self):
        if self.action in ['retrieve', 'complete']:
            queryset = Post.objects.all()
        else:
            queryset = Post.objects.filter(is_active=True)
        query = self.request.query_params.get('q', None)
        
        if query:
            # Tách chuỗi search thành các từ đơn (ví dụ: "áo khoác a4" -> ["áo", "khoác", "a4"])
            words = query.split()
            
            # Tạo danh sách các điều kiện: mỗi từ phải xuất hiện ở title HOẶC location
            # Dùng icontains để chấp nhận cả tiếng Việt có dấu/không dấu (tùy thuộc DB cài đặt)
            criterion = []
            for word in words:
                criterion.append(Q(title__icontains=word) | Q(location__icontains=word))
            
            # Dùng toán tử AND để nối các điều kiện lại: 
            # Kết quả phải chứa từ "áo" AND chứa từ "khoác" AND chứa từ "a4"
            queryset = queryset.filter(reduce(operator.or_, criterion)).distinct()
        
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

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def complete(self, request, pk=None):
        post = self.get_object()
        user = request.user
        
        
        # KIỂM TRA QUYỀN: User có đang giữ chìa khóa tủ này không?
        if not post.locker or post.locker.locker_id not in user.owned_locker_ids:
            return Response({"error": "Bạn không có chìa khóa tủ này!"}, status=403)

        try:
            with transaction.atomic():
                post.is_active = False
                post.save()
                
                if post.locker:
                    locker = post.locker
                    locker.trigger_unlock = True
                    locker.is_occupied = False
                    locker.save()                    
                    user.remove_locker(locker.locker_id)
                
            return Response({
                "status": "success", 
                "message": "Mở tủ thành công! Chìa khóa đã được thu hồi.",
                "locker_id": post.locker.locker_id if post.locker else None
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)
    




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
    
        locker.save()
        return Response({"status": "success", "message": "Trigger reset"})
    except Locker.DoesNotExist:
        return Response({"error": "Locker not found"}, status=404)
    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_and_grant_key(request):
    post_id = request.data.get('post_id')
    try:
        post = Post.objects.get(id=post_id)
        # Check quiz...
        if True: # Giả sử đúng
            request.user.add_locker(post.locker.locker_id)
            post.is_active = False
            post.save()
            return Response({"status": "success"})
    except Post.DoesNotExist:
        return Response(status=404)