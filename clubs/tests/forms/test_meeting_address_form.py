"""Unit tests of the meeting address form."""
import datetime

from clubs.forms import MeetingAddressForm
from clubs.models import Address, Club, MeetingAddress, User
from django.test import TestCase
from schedule.models import Calendar, Event, Rule


class MeetingAddressFormTestCase(TestCase):
    """Unit tests of the meeting address form."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_rules.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/default_address.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self.calendar = Calendar.objects.get(pk=5)
        self.club = Club.objects.get(pk=6)

        data = {
            'title': 'Exercise',
            'start': datetime.datetime(2008, 11, 5, 15, 0),
            'end': datetime.datetime(2008, 11, 5, 16, 30),
            'end_recurring_period': datetime.datetime(2009, 6, 1, 0, 0),
            'rule': Rule.objects.get(pk=9),
            'calendar': self.calendar
        }
        event = Event(**data)
        event.save()
        self.event = event

        self.address = Address.objects.get(pk=14)

        self.form_input = {
            'event': self.event,
            'address': self.address
        }

    def test_form_has_necessary_fields(self):
        form = MeetingAddressForm()
        self.assertIn('address', form.fields)

    def _create_test_events(self):
        "A valid address is one that has been used for other events in this calendar."

        data = {
            'title': 'Exercise',
            'start': datetime.datetime(2008, 11, 3, 8, 0),
            'end': datetime.datetime(2008, 11, 3, 9, 0),
            'end_recurring_period': datetime.datetime(2009, 6, 1, 0, 0),
            'rule': Rule.objects.get(pk=9),
            'calendar': self.calendar
        }
        event = Event(**data)
        event.save()

        meeting_address = MeetingAddress.objects.create(
            event=event,
            address=self.address
        )
