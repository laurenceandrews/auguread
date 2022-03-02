"""Unit tests for the MeetingLink model."""
import datetime

from clubs.models import Club, MeetingLink
from django.core.exceptions import ValidationError
from django.test import TestCase
from schedule.models import Calendar, Event, Rule


class MeetingLinkModelTestCase(TestCase):
    """Unit tests for the MeetingLink model."""

    fixtures = [
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_rules.json'
    ]

    def setUp(self):
        self.calendar = Calendar.objects.get(pk=5)

        # first event and meeting_link
        data = {
            'title': 'Exercise',
            'start': datetime.datetime(2008, 11, 3, 8, 0),
            'end': datetime.datetime(2008, 11, 3, 9, 0),
            'end_recurring_period': datetime.datetime(2009, 6, 1, 0, 0),
            'rule': Rule.objects.get(pk=9),
            'calendar': self.calendar
        }
        self.event = Event(**data)
        self.event.save()
        self.meeting_link = MeetingLink.objects.create(event=self.event,
                                                       meeting_link="https://www.google.com/")
        # second event and meeting_link
        data = {
            'title': 'Pay Mortgage',
            'start': datetime.datetime(2008, 11, 1, 14, 0),
            'end': datetime.datetime(2008, 11, 1, 14, 30),
            'end_recurring_period': datetime.datetime(2009, 10, 2, 0, 0),
            'rule': Rule.objects.get(pk=8),
            'calendar': self.calendar
        }
        self.second_event = Event(**data)
        self.second_event.save()
        self.second_meeting_link = MeetingLink.objects.create(event=self.second_event,
                                                              meeting_link="https://www.bing.com/")

    def test_valid_meeting_link(self):
        self._assert_meeting_link_is_valid()

    def test_event_cannot_be_blank(self):
        self.meeting_link.event = None
        self._assert_meeting_link_is_invalid()

    def test_event_must_be_unique(self):
        self.meeting_link.event = self.second_meeting_link.event
        self._assert_meeting_link_is_invalid()

    def test_link_cannot_be_blank(self):
        self.meeting_link.meeting_link = ''
        self._assert_meeting_link_is_invalid()

    def test_link_need_not_be_unique(self):
        self.meeting_link.meeting_link = self.second_meeting_link.meeting_link
        self._assert_meeting_link_is_valid()

    def _assert_meeting_link_is_valid(self):
        try:
            self.meeting_link.full_clean()
        except (ValidationError):
            self.fail('Test meeting address should be valid')

    def _assert_meeting_link_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.meeting_link.full_clean()
