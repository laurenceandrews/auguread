import datetime

from clubs.models import Address, Club, MeetingAddress, MeetingLink, User
from clubs.templatetags.event_meeting import event_meeting
from django.test import TestCase
from schedule.models import Calendar, Event, Rule


class EventMeetingTemplatetagTestCase(TestCase):

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/default_rules.json',
        'clubs/tests/fixtures/default_address.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.calendar = Calendar.objects.get(pk=5)
        self.club = Club.objects.get(pk=6)
        self._create_test_events()

    def test_valid_input_with_existing_meeting_address(self):
        result = event_meeting(self.event_with_meeting_address)
        self.assertEqual(result, self.meeting_address.address.full_address())

    def test_valid_input_with_existing_meeting_link(self):
        result = event_meeting(self.event_with_meeting_link)
        self.assertEqual(result, self.meeting_link.meeting_link)

    def test_valid_input_with_no_existing_meeting_address_or_link(self):
        result = event_meeting(self.event_with_no_link_or_address)
        self.assertEqual(result, None)

    def _create_test_events(self):
        data = {
            'title': 'Exercise',
            'start': datetime.datetime(2008, 11, 3, 8, 0),
            'end': datetime.datetime(2008, 11, 3, 9, 0),
            'end_recurring_period': datetime.datetime(2009, 6, 1, 0, 0),
            'rule': Rule.objects.get(pk=9),
            'calendar': self.calendar
        }
        self.event_with_meeting_address = Event(**data)
        self.event_with_meeting_address.save()
        address = Address.objects.get(pk=14)
        self.meeting_address = MeetingAddress.objects.create(event=self.event_with_meeting_address, address=address)

        data = {
            'title': 'Exercise',
            'start': datetime.datetime(2008, 11, 5, 15, 0),
            'end': datetime.datetime(2008, 11, 5, 16, 30),
            'end_recurring_period': datetime.datetime(2009, 6, 1, 0, 0),
            'rule': Rule.objects.get(pk=9),
            'calendar': self.calendar
        }
        self.event_with_meeting_link = Event(**data)
        self.event_with_meeting_link.save()
        self.meeting_link = MeetingLink.objects.create(event=self.event_with_meeting_link, meeting_link='https://zoom.us/test')

        data = {
            'title': 'Exercise',
            'start': datetime.datetime(2008, 11, 7, 8, 0),
            'end': datetime.datetime(2008, 11, 7, 9, 30),
            'end_recurring_period': datetime.datetime(2009, 6, 1, 0, 0),
            'rule': Rule.objects.get(pk=9),
            'calendar': self.calendar
        }
        self.event_with_no_link_or_address = Event(**data)
        self.event_with_no_link_or_address.save()
