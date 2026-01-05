from django.contrib import admin

# Register your models here.
from .models import Post,Locker
admin.site.register(Post)
admin.site.register(Locker)