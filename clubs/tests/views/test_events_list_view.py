import datetime

from clubs.models import Club, User
from django.test import TestCase
from django.urls import reverse
from schedule.models import Calendar, Event, Rule


class EventsListTest(TestCase):

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/default_rules.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.calendar = Calendar.objects.get(pk=5)
        self.club = Club.objects.get(pk=6)
        self.data = {'calendar_id': self.calendar.id}
        self.url = reverse(
            'events_list', kwargs={'calendar_id': self.data['calendar_id']}
        )

    def test_club_list_url(self):
        self.assertEqual(self.url,  f'/events_list/{self.calendar.id}')

    def test_get_club_list(self):
        self._create_test_events()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'events_list.html')
        self.assertEqual(len(response.context['events']), 7)

    def _create_test_events(self):
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

        data = {
            'title': 'Exercise',
            'start': datetime.datetime(2008, 11, 7, 8, 0),
            'end': datetime.datetime(2008, 11, 7, 9, 30),
            'end_recurring_period': datetime.datetime(2009, 6, 1, 0, 0),
            'rule': Rule.objects.get(pk=9),
            'calendar': self.calendar
        }
        event = Event(**data)
        event.save()

        data = {
            'title': 'Pay Mortgage',
            'start': datetime.datetime(2008, 11, 1, 14, 0),
            'end': datetime.datetime(2008, 11, 1, 14, 30),
            'end_recurring_period': datetime.datetime(2009, 10, 2, 0, 0),
            'rule': Rule.objects.get(pk=8),
            'calendar': self.calendar
        }
        event = Event(**data)
        event.save()

        data = {
            'title': "Rock's Birthday Party",
            'start': datetime.datetime(2008, 12, 11, 19, 0),
            'end': datetime.datetime(2008, 12, 11, 23, 59),
            'end_recurring_period': datetime.datetime(2009, 12, 22, 0, 0),
            'rule': Rule.objects.get(pk=7),
            'calendar': self.calendar
        }
        event = Event(**data)
        event.save()

        data = {
            'title': 'Christmas Party',
            'start': datetime.datetime(2008, 12, 25, 19, 30),
            'end': datetime.datetime(2008, 12, 25, 23, 59),
            'end_recurring_period': datetime.datetime(2010, 12, 31, 0, 0),
            'rule': Rule.objects.get(pk=7),
            'calendar': self.calendar
        }
        event = Event(**data)
        event.save()

        data = {
            'title': 'New Pinax site goes live',
            'start': datetime.datetime(2009, 1, 6, 11, 0),
            'end': datetime.datetime(2009, 1, 6, 12, 00),
            'end_recurring_period': datetime.datetime(2009, 1, 7, 0, 0),
            'calendar': self.calendar
        }
        event = Event(**data)
        event.save()
