"""Module imports"""
from clubs.models import Club_Users
from django import template
from schedule.models import Calendar, Event, Rule

register = template.Library()


@register.simple_tag
def get_club_user_id(club, user):
    """
    Returns the id of a club_user, or None
    Usage: {% get_club_user_id club user as club_user_id %}
    """

    club_user_id = None

    club_user = Club_Users.objects.filter(club=club, user=user)
    if club_user.exists():
        club_user = Club_Users.objects.get(club=club, user=user)
        club_user_id = club_user.id

    return club_user_id
