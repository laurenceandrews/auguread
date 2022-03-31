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

    def comments(self):
        comment_ids = PostComment.objects.filter(post=self).values_list('comment', flat=True)
        comments = Post.objects.filter(id__in=comment_ids)
        return comments


class ClubFeedPost(models.Model):
    """ClubFeed model used for recording posts made for a club's feed."""
    club = models.ForeignKey(Club, on_delete=models.CASCADE)

    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        """Model options."""
        verbose_name = "Club Feed Post"
        verbose_name_plural = "Club Feed Posts"


class PostComment(models.Model):
    """Comment model used for recording posts made as comments to other posts."""
    post = models.ForeignKey(Post, related_name='post', on_delete=models.CASCADE)

    comment = models.ForeignKey(Post, related_name='comment', on_delete=models.CASCADE)

    class Meta:
        """Model options."""
        verbose_name = "Post Comment"
        verbose_name_plural = "Post Comments"
