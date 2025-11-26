from django.conf import settings
from django.db import models
from django.utils import timezone


# Create your models here.
class Post(models.Model):
    post_id = models.AutoField(
        primary_key=True
    )  # 独自の主キーが欲しい場合。不要なら削除して default id を使う
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    context = models.TextField()
    like_count = models.PositiveIntegerField(default=0)
    time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "post"
        ordering = ["-time"]

    def __str__(self):
        return f"Post {self.post_id} by {self.user}"
