"""Unit tests for the MeetingAddress model."""
import datetime

from clubs.models import Address, MeetingAddress
from django.core.exceptions import ValidationError
from django.test import TestCase
from schedule.models import Calendar, Event, Rule


class MeetingAddressModelTestCase(TestCase):
    """Unit tests for the MeetingAddress model."""

    fixtures = [
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_rules.json',
        'clubs/tests/fixtures/default_address.json'
    ]

    def setUp(self):
        self.calendar = Calendar.objects.get(pk=5)
        self.address = Address.objects.get(pk=14)

        # first event and meeting_address
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
        self.meeting_address = MeetingAddress.objects.create(event=self.event,
                                                             address=self.address)
        # second event and meeting_address
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
        self.second_meeting_address = MeetingAddress.objects.create(event=self.second_event,
                                                                    address=self.address)

    def test_valid_meeting_address(self):
        self._assert_meeting_address_is_valid()

    def test_event_must_not_be_blank(self):
        self.meeting_address.event = None
        self._assert_meeting_address_is_invalid()

    def _assert_meeting_address_is_valid(self):
        try:
            self.meeting_address.full_clean()
        except (ValidationError):
            self.fail('Test meeting address should be valid')

    def _assert_meeting_address_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.meeting_address.full_clean()
