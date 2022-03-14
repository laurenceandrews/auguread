"""Tests for the event_update view."""
import datetime

from clubs.forms import CreateEventForm
from clubs.models import Club, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse
from schedule.models import Calendar, Event, Rule
from testfixtures import Replace, test_datetime
from testfixtures.tests.sample1 import str_now_1


class EventUpdateViewTest(TestCase):
    """Test suite for the event_update view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_rules.json',
        'clubs/tests/fixtures/default_club.json',
    ]

    def setUp(self):
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
            'edit_event', kwargs={'calendar_slug': self.calendar.slug, 'event_id': self.event.id}
        )

        self.form_input = {
            'title': 'Pay Mortgage'
        }

    def test_event_edit_url(self):
        self.assertEqual(self.url, f'/event/edit/{self.calendar.slug}/{self.event.id}/')

    def test_get_event_edit(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_update.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateEventForm))
        self.assertEqual(form.instance, self.event)

    def test_get_event_edit_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_unsuccesful_event_edit_update(self):
        self.client.login(email=self.user.email, password="Password123")
        self.form_input['title'] = ''
        before_count = Event.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Event.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_update.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateEventForm))
        self.assertTrue(form.is_bound)
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, 'Exercise')
        self.assertEqual(self.event.calendar, self.calendar)

    def test_post_event_edit_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
