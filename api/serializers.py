from rest_framework import serializers

from accounts.models import CustomUser, UserStats
from follow.models import Follow
from post.models import Like, Post


class UserStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStats
        fields = [
            "experience_points",
            "total_likes_received",
            "total_likes_given",
            "follower_count",
            "following_count",
            "post_count",
            "last_level_up",
            "updated_at",
        ]
        read_only_fields = fields


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    stats = UserStatsSerializer(read_only=True)
    rank = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            "user_id",
            "username",
            "user_name",
            "user_rank",
            "user_level",
            "user_mail",
            "password",
            "user_URL",
            "user_bio",
            "stats",
            "rank",
        ]
        read_only_fields = ["user_id", "stats", "rank"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    def get_rank(self, obj):
        rank = getattr(obj, "like_rank", None)
        if rank is not None:
            return rank
        stats = getattr(obj, "stats", None)
        if not stats:
            return None
        from accounts.models import UserStats  # local import to avoid cycle

        better_count = UserStats.objects.filter(
            total_likes_received__gt=stats.total_likes_received
        ).count()
        return better_count + 1


class PostSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source="user",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Post
        fields = [
            "post_id",
            "user",
            "user_id",
            "context",
            "like_count",
            "time",
        ]
        read_only_fields = ["post_id", "like_count", "time", "user"]


class FollowSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source="user",
        write_only=True,
        required=False,
        allow_null=True,
    )
    aim_user = CustomUserSerializer(read_only=True)
    aim_user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source="aim_user",
        write_only=True,
    )

    class Meta:
        model = Follow
        fields = [
            "id",
            "user",
            "user_id",
            "aim_user",
            "aim_user_id",
            "time",
        ]
        read_only_fields = ["id", "time", "user", "aim_user"]
        validators = []

    def validate(self, attrs):
        request = self.context.get("request")
        request_user = getattr(request, "user", None)
        user = attrs.get("user") or (
            request_user if getattr(request_user, "is_authenticated", False) else None
        )
        aim_user = attrs.get("aim_user") or getattr(self.instance, "aim_user", None)
        if not user or not aim_user:
            return attrs
        if user == aim_user:
            raise serializers.ValidationError("自分自身をフォローすることはできません。")
        existing = Follow.objects.filter(user=user, aim_user=aim_user)
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise serializers.ValidationError("既にフォロー済みです。")
        attrs["user"] = user
        return attrs


class LikeSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source="user",
        write_only=True,
        required=False,
        allow_null=True,
    )
    post = PostSerializer(read_only=True)
    post_id = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(),
        source="post",
        write_only=True,
    )

    class Meta:
        model = Like
        fields = [
            "id",
            "user",
            "user_id",
            "post",
            "post_id",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "user", "post"]
        validators = []

    def validate(self, attrs):
        request = self.context.get("request")
        request_user = getattr(request, "user", None)
        user = attrs.get("user") or (
            request_user if getattr(request_user, "is_authenticated", False) else None
        )
        post = attrs.get("post") or getattr(self.instance, "post", None)
        if not user or not post:
            return attrs
        if self.instance:
            return attrs
        exists = Like.objects.filter(user=user, post=post).exists()
        if exists:
            raise serializers.ValidationError("既にいいね済みです。")
        attrs["user"] = user
        return attrs
