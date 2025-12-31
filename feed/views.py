from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction 
from .models import Post
from .serializers import PostSerializer

class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Post.objects.filter(is_active=True).order_by('-created_at')

    # Gộp logic Create vào đây
    def create(self, request, *args, **kwargs):
        # 1. Check locker bận hay không ngay tại đây
        locker_id = request.data.get('locker_id')
        if locker_id and Post.objects.filter(locker_id=locker_id, is_active=True).exists():
            return Response(
                {"error": f"Tủ {locker_id} hiện đang bận. Chọn tủ khác đi bro!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Để Serializer lo phần còn lại (bao gồm cả việc tạo QuizQuestion)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                author = request.user if request.user.is_authenticated else None
                serializer.save(author=author) 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": "Lỗi server rồi!", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAuthenticated])
    def complete(self, request, pk=None):
        # ... Giữ nguyên logic complete của bro (rất tốt rồi)
        post = self.get_object()
        post.is_active = False
        post.save()
        return Response({"status": "success", "locker_id": getattr(post, 'locker_id', None)})