from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser):
    owned_locker_ids = models.JSONField(default=list, blank=True)

    def add_locker(self, locker_id):
        if locker_id not in self.owned_locker_ids:
            self.owned_locker_ids.append(locker_id)
            self.save()

    def remove_locker(self, locker_id):
        if locker_id in self.owned_locker_ids:
            self.owned_locker_ids.remove(locker_id)
            self.save()