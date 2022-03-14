"""Tests of the create_event_address view."""
import datetime

from clubs.models import Address, Club, MeetingAddress, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse
from schedule.models import Calendar, Event, Rule


class CreateEventAddressViewTest(TestCase):
    """Tests of the create_event_address view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_rules.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/default_address.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self.calendar = Calendar.objects.get(pk=5)
        self.club = Club.objects.get(pk=6)

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
        self.event = event

        self.address = Address.objects.get(pk=14)

        self.data = {
            'address': 14
        }
        self.url = reverse(
            'create_event_address', kwargs={'calendar_slug': self.calendar.slug, 'event_id': self.event.id}
        )

    def test_create_event_address_url(self):
        self.assertEqual(self.url, f'/event/address/create/{self.calendar.slug}/{self.event.id}/')

    def test_create_event_address_redirects_when_not_logged_in(self):
        meeting_address_count_before = MeetingAddress.objects.count()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        meeting_address_count_after = MeetingAddress.objects.count()
        self.assertEqual(meeting_address_count_after, meeting_address_count_before)

    def test_get_create_event_address(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_address_create.html')

    def test_successful_new_event_address(self):
        self.client.login(email=self.user.email, password="Password123")
        self._create_test_events()
        meeting_address_count_before = MeetingAddress.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        meeting_address_count_after = MeetingAddress.objects.count()
        self.assertEqual(meeting_address_count_after, meeting_address_count_before + 1)
        new_meeting_address = MeetingAddress.objects.get(event=self.event)
        self.assertEqual(self.address, new_meeting_address.address)
        response_url = reverse('full_calendar', kwargs={'calendar_slug': self.calendar.slug})
        self.assertTemplateUsed(response, 'fullcalendar.html')

    def test_unsuccessful_new_event_address(self):
        self.client.login(email=self.user.email, password="Password123")
        meeting_address_count_before = MeetingAddress.objects.count()
        self.data['address'] = ""
        response = self.client.post(self.url, self.data, follow=True)
        meeting_address_count_after = MeetingAddress.objects.count()
        self.assertEqual(meeting_address_count_after, meeting_address_count_before)
        self.assertTemplateUsed(response, 'event_address_create.html')

    def _create_test_events(self):
        "A valid address is one that has been used for other events in this calendar."

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

        meeting_address = MeetingAddress.objects.create(
            event=event,
            address=self.address
        )
