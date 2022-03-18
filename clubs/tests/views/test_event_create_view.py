"""Tests of the create_event view."""
import datetime

from clubs.models import Club, Club_Users, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse
from schedule.models import Calendar, Event, Rule


class CreateEventViewTest(TestCase):
    """Tests of the create_event view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_rules.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_clubs.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')

        self.calendar = Calendar.objects.get(pk=5)
        self.club = Club.objects.get(pk=6)
        self.data_for_club_event = {
            'title': 'Exercise',
            'start': '2022,01,01,11,00,00',
            'end': '2022,01,01,13,00,00',
            'end_recurring_period': '',
            'rule': '',
            'calendar': self.calendar
        }
        self.url = reverse(
            'create_event', kwargs={'calendar_slug': self.calendar.slug}
        )

    def test_create_online_event_url(self):
        self.assertEqual(self.url, f'/event/create/{self.calendar.slug}/')

    def test_create_event_redirects_when_not_logged_in(self):
        event_count_before = Event.objects.count()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.data_for_club_event, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        event_count_after = Event.objects.count()
        self.assertEqual(event_count_after, event_count_before)

    def test_create_event_redirects_when_not_a_club_owner(self):
        calendar_not_owner = Calendar.objects.get(pk=17)
        club_not_owner = Club.objects.get(pk=16)
        data_for_club_event_not_owner = {
            'title': 'Exercise',
            'start': '2022,01,01,11,00,00',
            'end': '2022,01,01,13,00,00',
            'end_recurring_period': '',
            'rule': '',
            'calendar': calendar_not_owner
        }
        url = reverse(
            'create_event', kwargs={'calendar_slug': calendar_not_owner.slug}
        )

        event_count_before = Event.objects.count()
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(url)
        redirect_url = reverse('full_calendar', kwargs={'calendar_slug': calendar_not_owner.slug})
        response = self.client.post(url, data_for_club_event_not_owner, follow=True)
        self.assertTemplateUsed(response, 'fullcalendar.html')
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        event_count_after = Event.objects.count()
        self.assertEqual(event_count_after, event_count_before)

    def test_get_create_event(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'event_create.html')
