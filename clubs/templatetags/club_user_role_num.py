"""Module imports"""
from clubs.models import Club_Users
from django import template
from schedule.models import Calendar, Event, Rule

register = template.Library()


@register.simple_tag
def club_user_role_num(club, user):
    """
    Returns the role_num of a club_user, or None
    Usage: {% club_user_role_num club user as role_num %}
    """

    role_num = None

    club_user = Club_Users.objects.filter(club=club, user=user)
    if club_user.exists():
        club_user = Club_Users.objects.get(club=club, user=user)
        role_num = club_user.role_num

    return role_num
