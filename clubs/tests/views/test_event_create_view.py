"""Tests of the create_event view."""
import datetime

import pytz
from clubs.models import Book, Club, Club_Book_History, Club_Users, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from schedule.models import Calendar, Event, Rule


class CreateEventViewTest(TestCase):
    """Tests of the create_event view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_rules.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_clubs.json',
        'clubs/tests/fixtures/default_book',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')

        self.calendar = Calendar.objects.get(pk=5)
        self.club = Club.objects.get(pk=6)
        self.url = reverse(
            'create_event', kwargs={'calendar_slug': self.calendar.slug}
        )

    def test_create_online_event_url(self):
        self.assertEqual(self.url, f'/event/create/{self.calendar.slug}/')

    def test_create_event_redirects_when_not_logged_in(self):
        form_input = {}
        event_count_before = Event.objects.count()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, form_input, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        event_count_after = Event.objects.count()
        self.assertEqual(event_count_after, event_count_before)

    def test_create_event_redirects_when_not_a_club_owner(self):
        calendar_not_owner = Calendar.objects.get(pk=17)
        club_not_owner = Club.objects.get(pk=16)
        form_input = {}
        url = reverse(
            'create_event', kwargs={'calendar_slug': calendar_not_owner.slug}
        )

        event_count_before = Event.objects.count()
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(url)
        redirect_url = reverse('full_calendar', kwargs={'calendar_slug': calendar_not_owner.slug})
        response = self.client.post(url, form_input, follow=True)
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

    def test_succesful_create_online_event(self):
        self.client.login(email=self.user.email, password="Password123")
        event_count_before = Event.objects.count()
        response = self.client.get(
            reverse("create_event", kwargs={"calendar_slug": f'{self.calendar.slug}'})
        )

        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse("create_event", kwargs={"calendar_slug": f'{self.calendar.slug}'}),
            {
                "description": "description",
                "title": "title",
                "end_recurring_period_1": "10:22:00",
                "end_recurring_period_0": "2008-10-30",
                "end_recurring_period_2": "AM",
                "end_1": "10:22:00",
                "end_0": "2008-10-30",
                "end_2": "AM",
                "start_0": "2008-10-30",
                "start_1": "09:21:57",
                "start_2": "AM",
            },
        )
        self.assertEqual(response.status_code, 302)
        event_count_after = Event.objects.count()
        self.assertEqual(event_count_after, event_count_before + 1)

    def test_succesful_create_in_person_event(self):
        calendar = Calendar.objects.get(pk=13)
        club = Club.objects.get(pk=12)
        book = Book.objects.get(pk=20)
        Club_Book_History.objects.create(club=club, book=book, average_rating=5)

        self.client.login(email=self.user.email, password="Password123")
        event_count_before = Event.objects.count()
        response = self.client.get(
            reverse("create_event", kwargs={"calendar_slug": f'{calendar.slug}'})
        )

        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse("create_event", kwargs={"calendar_slug": f'{calendar.slug}'}),
            {
                "description": "",
                "title": "title",
                "end_recurring_period_1": "10:22:00",
                "end_recurring_period_0": "2008-10-30",
                "end_recurring_period_2": "AM",
                "end_1": "10:22:00",
                "end_0": "2008-10-30",
                "end_2": "AM",
                "start_0": "2008-10-30",
                "start_1": "09:21:57",
                "start_2": "AM",
            },
        )
        self.assertEqual(response.status_code, 302)
        event_count_after = Event.objects.count()
        self.assertEqual(event_count_after, event_count_before + 1)

    def test_unsuccesful_create_event(self):
        self.client.login(email=self.user.email, password="Password123")
        event_count_before = Event.objects.count()
        response = self.client.get(
            reverse("create_event", kwargs={"calendar_slug": f'{self.calendar.slug}'})
        )

        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse("create_event", kwargs={"calendar_slug": f'{self.calendar.slug}'}),
            {
                "description": "description",
                "title": "",
                "end_recurring_period_1": "10:22:00",
                "end_recurring_period_0": "2008-10-30",
                "end_recurring_period_2": "AM",
                "end_1": "10:22:00",
                "end_0": "2008-10-30",
                "end_2": "AM",
                "start_0": "2008-10-30",
                "start_1": "09:21:57",
                "start_2": "AM",
            },
        )
        self.assertEqual(response.status_code, 200)
        event_count_after = Event.objects.count()
        self.assertEqual(event_count_after, event_count_before)
        self.assertTemplateUsed(response, 'event_create.html')
