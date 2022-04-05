"""Module imports"""
from clubs.models import Book_Rating
from django import template
from schedule.models import Calendar, Event, Rule

register = template.Library()


@register.simple_tag
def ratings_complete(user):
    """
    Returns a boolean of whether 10 or more positive ratings are complete
    """

    POSITIVE_RATINGS = [6, 7, 8, 9, 10]

    positive_ratings_complete = False

    positive_book_rating_count = Book_Rating.objects.filter(user = user, rating__in=POSITIVE_RATINGS).count()
    print(positive_book_rating_count)

    if positive_book_rating_count >= 5:
        positive_ratings_complete = True

    return positive_ratings_complete