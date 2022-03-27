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


class ClubFeedPost(models.Model):
    """ClubFeed model used for recording posts made for a club's feed."""
    club = models.ForeignKey(Club, on_delete=models.CASCADE)

    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        """Model options."""

    def post_count(self):
        """Returns the number of posts of self."""

        return self.posts.count()
