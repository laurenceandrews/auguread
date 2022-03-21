

from clubs.models.book_models import Book
from clubs.models.user_models import Club, Club_Users, User
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models


class Club_Books(models.Model):
    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        blank=False,
        default=0
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        blank=False,
        default=0
    )

    class Meta:
        app_label = "clubs"
        verbose_name = "Club Book"


class Club_Book_History(models.Model):
    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        blank=False,
        default=0
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        blank=False,
        default=0
    )

    average_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        blank=False,
        default=None
    )

    class Meta:
        app_label = "clubs"
        verbose_name = "Club Book History"
