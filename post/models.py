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
        indexes = [
            models.Index(fields=["-post_id"], name="post_latest_idx"),
            models.Index(fields=["-like_count", "-post_id"], name="post_ranking_idx"),
            models.Index(fields=["-time"], name="post_time_idx"),
        ]

    def __str__(self):
        return f"Post {self.post_id} by {self.user}"


class Like(models.Model):
    """User likes on posts."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "like"
        unique_together = ("user", "post")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "post"], name="like_user_post_idx"),
        ]

    def __str__(self):
        return f"Like<{self.user_id}:{self.post_id}>"
