"""Module imports"""
from clubs.models import Book_Rating
from django import template
from schedule.models import Calendar, Event, Rule

register = template.Library()


@register.simple_tag
def book_rated(book, user):
    """
    Returns a description of the rating of a BookRating of a book
    Usage: {% book_rated book user %}
    """

    rated_value = "Current rating: None"

    book_rating = Book_Rating.objects.filter(book=book, user=user)
    if book_rating.exists():
        book_rating = Book_Rating.objects.get(book=book, user=user)
        rating = book_rating.rating
        rated_value = "Current rating: " + rating

    return rated_value