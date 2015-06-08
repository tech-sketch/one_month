from django.db import models

from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    profile = models.CharField('プロフィール（仮）', max_length=512)
    # ユーザ名、名・性、メールアドレスなどはOAuthから取ってこれる