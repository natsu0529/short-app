from rest_framework import serializers

from accounts.models import CustomUser
from follow.models import Follow
from post.models import Post


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

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
            "good",
            "user_URL",
            "user_bio",
        ]
        read_only_fields = ["user_id", "good"]

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
            "good",
            "time",
        ]
        read_only_fields = ["post_id", "good", "time", "user"]


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
