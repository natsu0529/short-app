"""
FCM Push Notification Service

通知タイプ:
- liked: いいねされた時
- followed: フォローされた時
- level_up: レベルアップ時
- post_ranking: 投稿がトレンド/人気で10位以内
- user_ranking: ユーザーがランキングで10位以内
"""

import logging
from typing import Optional

from django.conf import settings

logger = logging.getLogger(__name__)

# Firebase Admin SDK (optional import)
try:
    import firebase_admin
    from firebase_admin import credentials, messaging

    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    firebase_admin = None
    messaging = None

_firebase_app = None


def _init_firebase():
    """Initialize Firebase Admin SDK if not already initialized."""
    global _firebase_app
    if not FIREBASE_AVAILABLE:
        logger.warning("firebase-admin is not installed. Push notifications disabled.")
        return False

    if _firebase_app is not None:
        return True

    cred_path = getattr(settings, "FIREBASE_CREDENTIALS_PATH", None)
    if not cred_path:
        logger.warning("FIREBASE_CREDENTIALS_PATH not set. Push notifications disabled.")
        return False

    try:
        cred = credentials.Certificate(cred_path)
        _firebase_app = firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin SDK initialized successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        return False


def send_push_notification(
    token: str,
    title: str,
    body: str,
    data: Optional[dict] = None,
) -> bool:
    """
    Send a push notification to a single device.

    Args:
        token: FCM device token
        title: Notification title
        body: Notification body
        data: Optional data payload

    Returns:
        True if sent successfully, False otherwise
    """
    if not _init_firebase():
        return False

    try:
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
            token=token,
        )
        response = messaging.send(message)
        logger.info(f"Push notification sent: {response}")
        return True
    except messaging.UnregisteredError:
        logger.warning(f"Token is unregistered: {token[:20]}...")
        _deactivate_token(token)
        return False
    except Exception as e:
        logger.error(f"Failed to send push notification: {e}")
        return False


def send_push_to_user(
    user_id: int,
    title: str,
    body: str,
    data: Optional[dict] = None,
    notification_type: Optional[str] = None,
) -> int:
    """
    Send push notification to all active devices of a user.

    Args:
        user_id: Target user ID
        title: Notification title
        body: Notification body
        data: Optional data payload
        notification_type: Type of notification (liked, followed, etc.)

    Returns:
        Number of successfully sent notifications
    """
    from accounts.models import DeviceToken

    tokens = DeviceToken.objects.filter(user_id=user_id, is_active=True)
    if not tokens.exists():
        return 0

    payload = data or {}
    if notification_type:
        payload["type"] = notification_type

    sent_count = 0
    for device in tokens:
        if send_push_notification(device.token, title, body, payload):
            sent_count += 1

    return sent_count


def _deactivate_token(token: str):
    """Mark a token as inactive when it's no longer valid."""
    from accounts.models import DeviceToken

    DeviceToken.objects.filter(token=token).update(is_active=False)


# --- Notification Helper Functions ---


def notify_liked(post_author_id: int, liker_username: str, post_context: str):
    """Notify when someone likes a post."""
    title = "いいね"
    body = f"{liker_username}さんがあなたの投稿にいいねしました"
    data = {"post_context": post_context[:50]}
    return send_push_to_user(post_author_id, title, body, data, "liked")


def notify_followed(target_user_id: int, follower_username: str):
    """Notify when someone follows the user."""
    title = "フォロー"
    body = f"{follower_username}さんがあなたをフォローしました"
    return send_push_to_user(target_user_id, title, body, None, "followed")


def notify_level_up(user_id: int, new_level: int):
    """Notify when user levels up."""
    title = "レベルアップ"
    body = f"レベル{new_level}に上がりました！"
    data = {"new_level": str(new_level)}
    return send_push_to_user(user_id, title, body, data, "level_up")


def notify_post_ranking(user_id: int, post_id: int, rank: int, ranking_type: str):
    """
    Notify when a post enters top 10 in rankings.

    Args:
        ranking_type: "trend" (24h) or "popular" (all-time)
    """
    type_name = "トレンド" if ranking_type == "trend" else "人気投稿"
    title = f"{type_name}ランキング入り"
    body = f"あなたの投稿が{type_name}ランキング{rank}位に入りました！"
    data = {"post_id": str(post_id), "rank": str(rank), "ranking_type": ranking_type}
    return send_push_to_user(user_id, title, body, data, "post_ranking")


def notify_user_ranking(user_id: int, rank: int, ranking_type: str):
    """
    Notify when user enters top 10 in rankings.

    Args:
        ranking_type: "level", "likes", or "followers"
    """
    type_names = {
        "level": "レベル",
        "likes": "いいね",
        "followers": "フォロワー",
    }
    type_name = type_names.get(ranking_type, ranking_type)
    title = f"{type_name}ランキング入り"
    body = f"{type_name}ランキングで{rank}位に入りました！"
    data = {"rank": str(rank), "ranking_type": ranking_type}
    return send_push_to_user(user_id, title, body, data, "user_ranking")


# --- Ranking Check Functions ---

RANKING_TOP_N = 10


def check_and_notify_post_ranking(post_id: int, user_id: int):
    """
    Check if a post is in top 10 of like rankings and notify.
    Called after a post receives a like.
    """
    from datetime import timedelta

    from django.utils import timezone

    from post.models import Post

    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return

    # Check trend ranking (24h)
    window = timezone.now() - timedelta(hours=24)
    trend_posts = list(
        Post.objects.filter(time__gte=window)
        .order_by("-like_count", "-time")
        .values_list("post_id", flat=True)[:RANKING_TOP_N]
    )
    if post_id in trend_posts:
        rank = trend_posts.index(post_id) + 1
        notify_post_ranking(user_id, post_id, rank, "trend")

    # Check popular ranking (all-time)
    popular_posts = list(
        Post.objects.order_by("-like_count", "-time")
        .values_list("post_id", flat=True)[:RANKING_TOP_N]
    )
    if post_id in popular_posts:
        rank = popular_posts.index(post_id) + 1
        notify_post_ranking(user_id, post_id, rank, "popular")


def check_and_notify_user_likes_ranking(user_id: int):
    """
    Check if user is in top 10 of likes ranking and notify.
    Called after a user receives a like.
    """
    from accounts.models import CustomUser

    top_users = list(
        CustomUser.objects.select_related("stats")
        .order_by("-stats__total_likes_received", "-date_joined")
        .values_list("user_id", flat=True)[:RANKING_TOP_N]
    )
    if user_id in top_users:
        rank = top_users.index(user_id) + 1
        notify_user_ranking(user_id, rank, "likes")


def check_and_notify_user_level_ranking(user_id: int):
    """
    Check if user is in top 10 of level ranking and notify.
    Called after a user levels up.
    """
    from accounts.models import CustomUser

    top_users = list(
        CustomUser.objects.order_by("-user_level", "-date_joined")
        .values_list("user_id", flat=True)[:RANKING_TOP_N]
    )
    if user_id in top_users:
        rank = top_users.index(user_id) + 1
        notify_user_ranking(user_id, rank, "level")


def check_and_notify_user_follower_ranking(user_id: int):
    """
    Check if user is in top 10 of follower ranking and notify.
    Called after a user gains a follower.
    """
    from accounts.models import CustomUser

    top_users = list(
        CustomUser.objects.select_related("stats")
        .order_by("-stats__follower_count", "-date_joined")
        .values_list("user_id", flat=True)[:RANKING_TOP_N]
    )
    if user_id in top_users:
        rank = top_users.index(user_id) + 1
        notify_user_ranking(user_id, rank, "followers")
