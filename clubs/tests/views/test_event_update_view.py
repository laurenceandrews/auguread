"""Tests for the event_update view."""
import datetime

from clubs.forms import CreateEventForm
from clubs.models import Club, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse
from schedule.models import Calendar, Event, Rule


class EventUpdateViewTest(TestCase):
    """Test suite for the event_update view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_rules.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_clubs.json'
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

    def test_get_event_edit_redirects_when_not_club_user(self):
        calendar = Calendar.objects.get(pk=17)
        club = Club.objects.get(pk=16)

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

        url = reverse(
            'edit_event', kwargs={'calendar_slug': calendar.slug, 'event_id': event.id}
        )

        self.client.login(email=self.user.email, password="Password123")
        redirect_url = reverse('full_calendar', kwargs={'calendar_slug': calendar.slug})
        response = self.client.post(url, data, follow=True)
        self.assertTemplateUsed(response, 'fullcalendar.html')
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )

    def test_succesful_event_edit_update_for_online_club(self):
        self.client.login(email=self.user.email, password="Password123")
        self.club.meeting_type = 'ONL'
        self.club.save()
        before_count = Event.objects.count()
        form_input = {
            "title": "title",
            "end_1": "10:22:00",
            "end_0": "2008-10-30",
            "end_2": "AM",
            "start_0": "2008-10-30",
            "start_1": "09:21:57",
            "start_2": "AM",
        }
        response = self.client.post(self.url, form_input)
        after_count = Event.objects.count()
        self.assertEqual(after_count, before_count)

    def test_succesful_event_edit_update_for_in_person_club(self):
        calendar = Calendar.objects.get(pk=13)
        club = Club.objects.get(pk=12)
        club.meeting_type = 'INP'
        club.save()
        data = {
            'title': 'Exercise',
            'start': datetime.datetime(2008, 11, 3, 8, 0),
            'end': datetime.datetime(2008, 11, 3, 9, 0),
            'end_recurring_period': datetime.datetime(2009, 6, 1, 0, 0),
            'rule': Rule.objects.get(pk=9),
            'calendar': calendar
        }
        event = Event(**data)
        event.save()

        url = reverse(
            'edit_event', kwargs={'calendar_slug': calendar.slug, 'event_id': event.id}
        )

        self.client.login(email=self.user.email, password="Password123")
        before_count = Event.objects.count()
        form_input = {
            "title": "title",
            "end_1": "10:22:00",
            "end_0": "2008-10-30",
            "end_2": "AM",
            "start_0": "2008-10-30",
            "start_1": "09:21:57",
            "start_2": "AM",
        }
        response = self.client.post(url, form_input)
        after_count = Event.objects.count()
        self.assertEqual(after_count, before_count)

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
