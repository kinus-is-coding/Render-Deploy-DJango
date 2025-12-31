from django.db import models

# Create your models here.

from django.conf import settings


class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, # Recommended: Set author to NULL instead of CASCADE deleting posts
        null=True,                 # Allows NULL in the database
        blank=True                 # Allows the form field to be empty
    )
    title = models.CharField(max_length=255)
    location = models.TextField()
    image_url = models.URLField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    locker_id = models.CharField(max_length=10, blank=True, null=True, db_index=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
    
        if self.is_active and self.locker_id:
            # Tìm xem có bài nào KHÁC bài này, cùng locker và đang Active không
            exists = Post.objects.filter(
                locker_id=self.locker_id, 
                is_active=True
            ).exclude(pk=self.pk).exists()
            
            if exists:
                raise ValueError(f"Locker {self.locker_id} hiện đang có người sử dụng!")

        super().save(*args, **kwargs)
class QuizQuestion(models.Model):
    post = models.ForeignKey(Post, related_name='quiz_questions', on_delete=models.CASCADE)
    
    question_text = models.TextField()
    
    # Store the choices as a JSON array (list of {id: 'a', text: 'choice'})
    choices_json = models.JSONField() 
    
    # Store the correct answer ID ('a', 'b', 'c', or 'd')
    correct_choice_id = models.CharField(max_length=10) 
    
    def __str__(self):
        return f"Q for Post {self.post.id}: {self.question_text[:30]}..."