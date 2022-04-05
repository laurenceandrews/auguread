"""Tests of the event_detail view."""
import datetime

from clubs.models import Club, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse
from schedule.models import Calendar, Event, Rule


class EventDetailViewTest(TestCase):
    """Tests of the event_detail view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_rules.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_clubs.json',
        'clubs/tests/fixtures/default_book.json',
        'clubs/tests/fixtures/other_books.json',
        'clubs/tests/fixtures/seven_pos_ratings.json'
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

        self.url = reverse(
            'event_detail', kwargs={'calendar_slug': self.calendar.slug, 'event_id': self.event.id}
        )

    def test_event_detail_url(self):
        self.assertEqual(self.url, f'/event/detail/{self.calendar.slug}/{self.event.id}/')

    def test_get_event_detail_with_valid_id(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_detail.html')
        event = response.context['event']
        self.assertEquals(event, self.event)

    def test_get_event_detail_with_valid_id_and_in_person(self):
        self.client.login(email=self.user.email, password="Password123")
        self.club.meeting_type = 'INP'
        self.club.save()
        self.club.refresh_from_db()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_detail.html')
        event = response.context['event']
        self.assertEquals(event, self.event)

    def test_get_event_detail_with_invalid_id(self):
        self.client.login(email=self.user.email, password="Password123")
        url = reverse('event_detail', kwargs={'calendar_slug': self.calendar.slug, 'event_id': 0})
        response = self.client.get(url, follow=True)
        response_url = reverse('full_calendar', kwargs={'calendar_slug': self.calendar.slug})
        self.assertTemplateUsed(response, 'fullcalendar.html')

    def test_get_event_detail_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_full_calendar_as_owner(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_detail.html')

    def test_get_full_calendar_as_non_owner(self):
        user = User.objects.get(pk=2)
        self.client.login(email=user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_detail.html')
