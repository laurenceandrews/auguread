"""Module imports"""
from clubs.models import MeetingAddress, MeetingLink
from django import template
from schedule.models import Calendar, Event, Rule

register = template.Library()


@register.simple_tag
def event_meeting(event):
    """
    Returns the MeetingAddress or MeetingLink for the event, or None
    Usage: {% event_meeting event %}
    """

    event_meeting = None

    meeting_address = MeetingAddress.objects.filter(event=event)
    if meeting_address.exists():
        meeting_address = MeetingAddress.objects.get(event=event)
        event_meeting = meeting_address.full_address
    else:
        meeting_link = MeetingLink.objects.filter(event=event)
        if meeting_link.exists():
            meeting_link = MeetingLink.objects.get(event=event)
            event_meeting = meeting_link.meeting_link

    return event_meeting
