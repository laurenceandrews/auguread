from clubs.models.user_models import Club, User
from django.db import models


class Post(models.Model):
    """Posts by users."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    text = models.CharField(
        max_length=280
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        """Model options."""
        app_label = "clubs"
        ordering = ['-created_at']


class ClubFeed(models.Model):
    """ClubFeed model used for recording posts made for a club's feed."""
    club = models.OneToOneField(
        Club,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    posts = models.ManyToManyField(Post)

    class Meta:
        """Model options."""
