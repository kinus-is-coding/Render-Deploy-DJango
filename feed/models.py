from django.db import models
from django.conf import settings

# 1. THÊM BẢNG LOCKER: Quản lý cái tủ thật ở ngoài đời
class Locker(models.Model):
    locker_id = models.CharField(max_length=10, unique=True)
    is_occupied = models.BooleanField(default=False)
    trigger_unlock = models.BooleanField(default=False)   # CÔNG TẮC CHO ESP32

    def __str__(self):
        return f"Tủ số {self.locker_id} ({'Đầy' if self.is_occupied else 'Trống'})"

class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,                 
        blank=True                 
    )
    title = models.CharField(max_length=255)
    location = models.TextField()
    image_url = models.URLField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    locker = models.ForeignKey(Locker, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.is_active and self.locker:
            exists = Post.objects.filter(
                locker=self.locker, 
                is_active=True
            ).exclude(pk=self.pk).exists()
            
            if exists:
                raise ValueError(f"Locker {self.locker.locker_id} hiện đang có người sử dụng!")

            if not self.pk:
                # 1. Đánh dấu tủ đã bị chiếm
                self.locker.is_occupied = True
                # 2. Bật công tắc mở khóa cho ESP32
                self.locker.trigger_unlock = True
                self.locker.save()

        super().save(*args, **kwargs)

class QuizQuestion(models.Model):
    post = models.ForeignKey(Post, related_name='quiz_questions', on_delete=models.CASCADE)
    question_text = models.TextField()
    choices_json = models.JSONField() 
    correct_choice_id = models.CharField(max_length=10) 
    
    def __str__(self):
        return f"Q for Post {self.post.id}: {self.question_text[:30]}..."