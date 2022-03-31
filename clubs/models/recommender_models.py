"""Models in the clubs app."""

import uuid

from clubs.models.book_models import Book
from clubs.models.user_models import Club
from django.db import models


class MyUUIDModel(models.Model):
    class Meta:
        app_label = "clubs"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )


class ClubBookRecommendation(models.Model):
    """Recommended book for a club."""
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE
    )

    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE
    )

    class Meta:
        """Model options."""
        verbose_name = "Club Book Recommendation"
        verbose_name_plural = "Club Book Recommendations"
