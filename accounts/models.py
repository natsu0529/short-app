from django.db import models

# Create your models here.
# accounts/models.py
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=50)
    user_rank = models.CharField(max_length=20, blank=True)
    user_level = models.PositiveIntegerField(default=1)
    user_mail = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # AbstractUser ですでにあるので省略可
    good = models.PositiveIntegerField(default=0)
    user_URL = models.URLField(blank=True)
    user_bio = models.TextField(blank=True)
