import pytest


@pytest.mark.django_db
def test_user_stats_auto_created(user):
    stats = user.stats

    assert stats.experience_points == 0
    assert stats.total_likes_received == 0
    assert stats.post_count == 0


@pytest.mark.django_db
def test_user_stats_level_up_and_experience(user):
    stats = user.stats

    # 新アルゴリズム: 10 EXPでレベル2
    stats.gain_experience(10)
    stats.refresh_from_db()
    user.refresh_from_db()

    assert stats.experience_points == 10
    assert user.user_level == 2
    assert stats.last_level_up is not None


@pytest.mark.django_db
def test_user_stats_counters_update(user):
    stats = user.stats

    stats.register_post_created()
    stats.register_like_given()
    stats.register_like_received(value=3)
    stats.update_follow_counts(followers_delta=2, following_delta=1)
    stats.update_follow_counts(followers_delta=-10, following_delta=-10)

    stats.refresh_from_db()

    assert stats.post_count == 1
    assert stats.total_likes_given == 1
    assert stats.total_likes_received == 3
    assert stats.follower_count == 0
    assert stats.following_count == 0
