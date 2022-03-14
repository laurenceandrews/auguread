"""Tests of the create_event_link view."""
import datetime

from clubs.models import Club, MeetingLink, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse
from schedule.models import Calendar, Event, Rule


class CreateEventLinkViewTest(TestCase):
    """Tests of the create_event_link view."""

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
        event = Event(**data)
        event.save()
        self.event = event

        self.data = {
            'meeting_link': 'https://zoom.us/test'
        }
        self.url = reverse(
            'create_event_link', kwargs={'calendar_slug': self.calendar.slug, 'event_id': self.event.id}
        )

    def test_create_event_link_url(self):
        self.assertEqual(self.url, f'/event/link/create/{self.calendar.slug}/{self.event.id}/')

    def test_create_event_link_redirects_when_not_logged_in(self):
        meeting_link_count_before = MeetingLink.objects.count()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        meeting_link_count_after = MeetingLink.objects.count()
        self.assertEqual(meeting_link_count_after, meeting_link_count_before)

    def test_get_create_event_link(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_link_create.html')

    def test_successful_new_event_link(self):
        self.client.login(email=self.user.email, password="Password123")
        meeting_link_count_before = MeetingLink.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        meeting_link_count_after = MeetingLink.objects.count()
        self.assertEqual(meeting_link_count_after, meeting_link_count_before + 1)
        new_meeting_link = MeetingLink.objects.get(event=self.event)
        self.assertEqual(self.data['meeting_link'], new_meeting_link.meeting_link)
        response_url = reverse('full_calendar', kwargs={'calendar_slug': self.calendar.slug})
        self.assertTemplateUsed(response, 'fullcalendar.html')

    def test_unsuccessful_new_event_link(self):
        self.client.login(email=self.user.email, password="Password123")
        meeting_link_count_before = MeetingLink.objects.count()
        self.data['meeting_link'] = ""
        response = self.client.post(self.url, self.data, follow=True)
        meeting_link_count_after = MeetingLink.objects.count()
        self.assertEqual(meeting_link_count_after, meeting_link_count_before)
        self.assertTemplateUsed(response, 'event_link_create.html')
