"""Tests of the create_event view."""
import datetime

from clubs.models import Club, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse
from schedule.models import Calendar, Event, Rule


class CreateEventViewTest(TestCase):
    """Tests of the create_event view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_rules.json',
        'clubs/tests/fixtures/default_club.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')

        self.default_meeting_start = datetime.datetime.now()
        default_meeting_lenth_in_hours = 1
        default_meeting_lenth_delta = datetime.timedelta(hours=default_meeting_lenth_in_hours)
        self.default_meeting_end = self.default_meeting_start + default_meeting_lenth_delta

        self.calendar_for_online_club = Calendar.objects.get(pk=5)
        self.online_club = Club.objects.get(pk=6)
        self.data_for_online_club_event = {
            'title': 'Exercise',
            'start': '2022,01,01,11,00,00',
            'end': '2022,01,01,13,00,00',
            'end_recurring_period': '',
            'rule': '',
            'calendar': self.calendar_for_online_club
        }
        self.url_for_online_club = reverse(
            'create_event', kwargs={'calendar_id': self.calendar_for_online_club.id}
        )

    def test_create_online_event_url(self):
        self.assertEqual(self.url_for_online_club, f'/event/create/{self.calendar_for_online_club.id}/')

    def test_create_event_redirects_when_not_logged_in(self):
        event_count_before = Event.objects.count()
        redirect_url = reverse_with_next('log_in', self.url_for_online_club)
        response = self.client.post(self.url_for_online_club, self.data_for_online_club_event, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        event_count_after = Event.objects.count()
        self.assertEqual(event_count_after, event_count_before)

    def test_get_create_event(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url_for_online_club)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_create.html')
