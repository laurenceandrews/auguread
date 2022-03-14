"""Tests of the delete_event view."""
import datetime

from clubs.models import Club, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse
from schedule.models import Calendar, Event, Rule


class DeleteEventViewTest(TestCase):
    """Tests of the delete_event view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_rules.json',
        'clubs/tests/fixtures/default_club.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self.calendar = Calendar.objects.get(pk=5)
        self.club = Club.objects.get(pk=6)

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

        self.data = {}

        self.url = reverse(
            'delete_event', kwargs={'calendar_slug': self.calendar.slug, 'event_id': self.event.id}
        )

    def test_delete_event_url(self):
        self.assertEqual(self.url, f'/event/delete/{self.calendar.slug}/{self.event.id}/')

    def test_delete_event_redirects_when_not_logged_in(self):
        event_count_before = Event.objects.count()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        event_count_after = Event.objects.count()
        self.assertEqual(event_count_after, event_count_before)

    def test_get_delete_event(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_delete.html')
        self.assertEqual(response.context['event'], self.event)
