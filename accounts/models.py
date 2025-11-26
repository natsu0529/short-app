from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class CustomUser(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=50)
    user_rank = models.CharField(max_length=20, blank=True)
    user_level = models.PositiveIntegerField(default=1)
    user_mail = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # AbstractUser ですでにあるので省略可
    user_URL = models.URLField(blank=True)
    user_bio = models.TextField(blank=True)


class UserStats(models.Model):
    """Aggregated counters that power ranking features."""

    LEVEL_UP_STEP = 100
    LIKE_GAIN_EXP = 2
    LIKE_RECEIVE_EXP = 5
    POST_CREATE_EXP = 10

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="stats",
    )
    experience_points = models.PositiveIntegerField(default=0)
    total_likes_received = models.PositiveIntegerField(default=0)
    total_likes_given = models.PositiveIntegerField(default=0)
    follower_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    post_count = models.PositiveIntegerField(default=0)
    last_level_up = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_stats"

    def __str__(self) -> str:  # pragma: no cover - readable admin value
        return f"Stats<{self.user_id}>"

    def _apply_level_up_if_needed(self):
        if not hasattr(self, "user"):
            return
        expected_level = max(1, self.experience_points // self.LEVEL_UP_STEP + 1)
        if expected_level > self.user.user_level:
            self.user.user_level = expected_level
            self.user.save(update_fields=["user_level"])
            self.last_level_up = timezone.now()

    def gain_experience(self, points: int):
        if points <= 0:
            return
        self.experience_points += points
        self._apply_level_up_if_needed()
        self.save(update_fields=["experience_points", "last_level_up"])

    def register_post_created(self):
        self.post_count += 1
        self.save(update_fields=["post_count"])
        self.gain_experience(self.POST_CREATE_EXP)

    def register_like_given(self, *, value: int = 1):
        if value <= 0:
            return
        self.total_likes_given += value
        self.save(update_fields=["total_likes_given"])
        self.gain_experience(self.LIKE_GAIN_EXP * value)

    def register_like_received(self, *, value: int = 1):
        if value <= 0:
            return
        self.total_likes_received += value
        self.save(update_fields=["total_likes_received"])
        self.gain_experience(self.LIKE_RECEIVE_EXP * value)

    def update_follow_counts(self, *, followers_delta: int = 0, following_delta: int = 0):
        if followers_delta:
            self.follower_count = max(0, self.follower_count + followers_delta)
        if following_delta:
            self.following_count = max(0, self.following_count + following_delta)
        self.save(update_fields=["follower_count", "following_count"])


@receiver(post_save, sender=CustomUser)
def ensure_user_stats(sender, instance: CustomUser, created: bool, **_: object):
    """Ensure every user always has a stats row."""

    if created:
        UserStats.objects.create(user=instance)
    else:
        UserStats.objects.get_or_create(user=instance)
