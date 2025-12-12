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
    apple_user_id = models.CharField(max_length=255, unique=True, null=True, blank=True, db_index=True)


class UserStats(models.Model):
    """Aggregated counters that power ranking features."""

    LIKE_GAIN_EXP = 2
    LIKE_RECEIVE_EXP = 5
    POST_CREATE_EXP = 10

    # レベルごとの必要経験値閾値
    # レベル1: 0, レベル2: 10, レベル3: 30, レベル4: 60, レベル5: 100
    # レベル6-10: 50ずつ増加 (150, 200, 250, 300, 350)
    # レベル11-20: 100ずつ増加 (450, 550, ..., 1350)
    # レベル21-50: 200ずつ増加 (1550, 1750, ..., 7350)
    # レベル51-100: 300ずつ増加 (7650, 7950, ..., 22350)
    # レベル101以降: 500ずつ増加

    @staticmethod
    def calculate_level_from_exp(exp: int) -> int:
        """経験値からレベルを計算する"""
        if exp < 10:
            return 1
        if exp < 30:
            return 2
        if exp < 60:
            return 3
        if exp < 100:
            return 4
        if exp < 150:
            return 5

        # レベル6-9: 50ずつ (150, 200, 250, 300)
        if exp < 350:
            return 6 + (exp - 150) // 50

        # レベル10: 350-449
        if exp < 450:
            return 10

        # レベル11-20: 100ずつ (450, 550, ..., 1350)
        if exp < 1450:
            return 11 + (exp - 450) // 100

        # レベル20: 1350-1549
        if exp < 1550:
            return 20

        # レベル21-50: 200ずつ (1550, 1750, ..., 7350)
        if exp < 7350:
            return 21 + (exp - 1550) // 200

        # レベル50: 7150-7649
        if exp < 7650:
            return 50

        # レベル51-100: 300ずつ (7650, 7950, ..., 22350)
        if exp < 22350:
            return 51 + (exp - 7650) // 300

        # レベル100: 22050-22849
        if exp < 22850:
            return 100

        # レベル101以降: 500ずつ
        return 101 + (exp - 22850) // 500

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
        expected_level = self.calculate_level_from_exp(self.experience_points)
        if expected_level > self.user.user_level:
            old_level = self.user.user_level
            self.user.user_level = expected_level
            self.user.save(update_fields=["user_level"])
            self.last_level_up = timezone.now()

            # Send push notification for level up
            from api.services.notifications import (
                check_and_notify_user_level_ranking,
                notify_level_up,
            )

            notify_level_up(user_id=self.user.user_id, new_level=expected_level)
            # Check level ranking notification
            check_and_notify_user_level_ranking(self.user.user_id)

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


class DeviceToken(models.Model):
    """FCM device tokens for push notifications."""

    PLATFORM_IOS = "ios"
    PLATFORM_ANDROID = "android"
    PLATFORM_CHOICES = [
        (PLATFORM_IOS, "iOS"),
        (PLATFORM_ANDROID, "Android"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="device_tokens",
    )
    token = models.CharField(max_length=255, unique=True)
    platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "device_tokens"

    def __str__(self) -> str:
        return f"DeviceToken<{self.user_id}:{self.platform}>"
