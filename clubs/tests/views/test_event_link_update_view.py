"""Tests for the event_link_update view."""
import datetime

from clubs.forms import MeetingLinkForm
from clubs.models import Club, MeetingLink, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse
from schedule.models import Calendar, Event, Rule


class EventLinkUpdateViewTest(TestCase):
    """Test suite for the event_link_update view."""

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

        self.meeting_link = MeetingLink.objects.create(event=self.event, meeting_link='https://zoom.us/test')

        self.url = reverse(
            'edit_event_link', kwargs={'calendar_slug': self.calendar.slug, 'event_id': self.event.id}
        )

        self.form_input = {
            'meeting_link': 'https://meet.google.com/xxx-yyyy-zzz'
        }

    def test_event_link_edit_url(self):
        self.assertEqual(self.url, f'/event/link/edit/{self.calendar.slug}/{self.event.id}/')

    def test_get_event_link_edit(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_link_update.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, MeetingLinkForm))
        self.assertEqual(form.instance, self.event)

    def test_get_event_link_edit_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_event_link_edit_redirects_when_not_club_owner(self):
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
            'edit_event_link', kwargs={'calendar_slug': calendar.slug, 'event_id': event.id}
        )

        self.client.login(email=self.user.email, password="Password123")
        redirect_url = reverse('full_calendar', kwargs={'calendar_slug': calendar.slug})
        response = self.client.post(url, data, follow=True)
        self.assertTemplateUsed(response, 'fullcalendar.html')
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )

    def test_succesful_event_link_edit_update(self):
        self.client.login(email=self.user.email, password="Password123")
        before_count = MeetingLink.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = MeetingLink.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fullcalendar.html')

    def test_succesful_event_link_edit_when_meeting_link_already_exists(self):
        self.client.login(email=self.user.email, password="Password123")
        before_count = Event.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Event.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fullcalendar.html')

    def test_succesful_event_link_edit_when_meeting_link_does_not_already_exists(self):
        self.meeting_link.delete()
        self.client.login(email=self.user.email, password="Password123")
        before_count = Event.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Event.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fullcalendar.html')

    def test_unsuccesful_event_link_edit_update(self):
        self.client.login(email=self.user.email, password="Password123")
        self.form_input['meeting_link'] = ''
        before_count = MeetingLink.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = MeetingLink.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_link_update.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, MeetingLinkForm))
        self.assertTrue(form.is_bound)
        self.meeting_link.refresh_from_db()
        self.assertEqual(self.meeting_link.meeting_link, 'https://zoom.us/test')

    def test_post_event_link_edit_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
