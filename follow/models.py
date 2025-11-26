from django.conf import settings
from django.db import models


class Follow(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="following", on_delete=models.CASCADE
    )
    aim_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="followers", on_delete=models.CASCADE
    )
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "follow"
        unique_together = ("user", "aim_user")
