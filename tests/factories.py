import factory
from django.utils import timezone

from accounts.models import CustomUser, UserStats
from follow.models import Follow
from post.models import Post


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser

    username = factory.Sequence(lambda n: f"user{n}")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    user_name = factory.LazyAttribute(lambda obj: obj.username.title())
    user_mail = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")

    @factory.post_generation
    def stats(self, create, extracted, **kwargs):
        if not create:
            return
        stats = self.stats  # ensure creation via signal
        for key, value in (extracted or kwargs or {}).items():
            setattr(stats, key, value)
        stats.save()


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    user = factory.SubFactory(UserFactory)
    context = factory.Faker("sentence")
    like_count = 0
    time = factory.LazyFunction(timezone.now)


class FollowFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Follow
        django_get_or_create = ("user", "aim_user")

    user = factory.SubFactory(UserFactory)
    aim_user = factory.SubFactory(UserFactory)
