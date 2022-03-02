"""Unit tests for the MeetingAddress model."""
import datetime

from clubs.models import Club, MeetingAddress
from django.core.exceptions import ValidationError
from django.test import TestCase
from schedule.models import Calendar, Event, Rule


class MeetingAddressModelTestCase(TestCase):
    """Unit tests for the MeetingAddress model."""

    fixtures = [
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_rules.json'
    ]

    def setUp(self):
        self.calendar = Calendar.objects.get(pk=5)

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
                                                             name="City Library",
                                                             address1="Palm Street",
                                                             address2="Clifton",
                                                             zip_code=00000,
                                                             city="London",
                                                             country="GB")
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
                                                                    name="Grove Park",
                                                                    address1="Butterfly Lane",
                                                                    address2="Landon",
                                                                    zip_code=55555,
                                                                    city="London",
                                                                    country="GB")

    def test_valid_meeting_address(self):
        self._assert_meeting_address_is_valid()

    def test_event_cannot_be_blank(self):
        self.meeting_address.event = None
        self._assert_meeting_address_is_invalid()

    def test_event_must_be_unique(self):
        self.meeting_address.event = self.second_meeting_address.event
        self._assert_meeting_address_is_invalid()

    def test_name_cannot_be_blank(self):
        self.meeting_address.name = ''
        self._assert_meeting_address_is_invalid()

    def test_name_can_be_1024_characters_long(self):
        self.meeting_address.name = 'x' * 1024
        self._assert_meeting_address_is_valid()

    def test_name_cannot_be_over_1024_characters_long(self):
        self.meeting_address.name = 'x' + 'x' * 1024
        self._assert_meeting_address_is_invalid()

    def test_name_need_not_be_unique(self):
        self.meeting_address.name = self.second_meeting_address.name
        self._assert_meeting_address_is_valid()

    def test_address1_cannot_be_blank(self):
        self.meeting_address.address1 = ''
        self._assert_meeting_address_is_invalid()

    def test_address1_can_be_1024_characters_long(self):
        self.meeting_address.address1 = 'x' * 1024
        self._assert_meeting_address_is_valid()

    def test_address1_cannot_be_over_1024_characters_long(self):
        self.meeting_address.address1 = 'x' + 'x' * 1024
        self._assert_meeting_address_is_invalid()

    def test_address1_need_not_be_unique(self):
        self.meeting_address.address1 = self.second_meeting_address.address1
        self._assert_meeting_address_is_valid()

    def test_address2_may_be_blank(self):
        self.meeting_address.address2 = ''
        self._assert_meeting_address_is_valid()

    def test_address2_can_be_1024_characters_long(self):
        self.meeting_address.address1 = 'x' * 1024
        self._assert_meeting_address_is_valid()

    def test_address2_cannot_be_over_1024_characters_long(self):
        self.meeting_address.address1 = 'x' + 'x' * 1024
        self._assert_meeting_address_is_invalid()

    def test_address2_need_not_be_unique(self):
        self.meeting_address.address2 = self.second_meeting_address.address2
        self._assert_meeting_address_is_valid()

    def test_zip_code_may_be_blank(self):
        self.meeting_address.zip_code = ''
        self._assert_meeting_address_is_valid()

    def test_zip_code_can_be_12_characters_long(self):
        self.meeting_address.zip_code = 'x' * 12
        self._assert_meeting_address_is_valid()

    def test_zip_code_cannot_be_over_12_characters_long(self):
        self.meeting_address.zip_code = 'x' + 'x' * 12
        self._assert_meeting_address_is_invalid()

    def test_zip_code_need_not_be_unique(self):
        self.meeting_address.zip_code = self.second_meeting_address.zip_code
        self._assert_meeting_address_is_valid()

    def test_city_cannot_be_blank(self):
        self.meeting_address.city = ''
        self._assert_meeting_address_is_invalid()

    def test_city_can_be_1024_characters_long(self):
        self.meeting_address.city = 'x' * 1024
        self._assert_meeting_address_is_valid()

    def test_city_cannot_be_over_1024_characters_long(self):
        self.meeting_address.city = 'x' + 'x' * 1024
        self._assert_meeting_address_is_invalid()

    def test_city_need_not_be_unique(self):
        self.meeting_address.city = self.second_meeting_address.city
        self._assert_meeting_address_is_valid()

    def test_city_cannot_be_blank(self):
        self.meeting_address.country = ''
        self._assert_meeting_address_is_invalid()

    def test_country_need_not_be_unique(self):
        self.meeting_address.country = self.second_meeting_address.country
        self._assert_meeting_address_is_valid()

    def _assert_meeting_address_is_valid(self):
        try:
            self.meeting_address.full_clean()
        except (ValidationError):
            self.fail('Test meeting address should be valid')

    def _assert_meeting_address_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.meeting_address.full_clean()
