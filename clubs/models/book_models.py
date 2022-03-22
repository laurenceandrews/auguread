
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models


class Book(models.Model):
    ISBN = models.CharField(
        max_length=10,
        blank=False
    )

    title = models.CharField(
        max_length=250,
        blank=False
    )

    author = models.CharField(
        max_length=300,
        blank=False
    )

    publisher = models.CharField(
        max_length=300,
        blank=False
    )

    publication_year = models.IntegerField(
        blank=False
    )

    image_small = models.ImageField(
        blank=False,
        default='/static/default_book.png/'
    )

    image_medium = models.ImageField(
        blank=False,
        default='/static/default_book.png/'
    )

    image_large = models.ImageField(
        blank=False,
        default='/static/default_book.png/'
    )

    class Meta:
        app_label = "clubs"

    def __str__(self):
        return self.title
