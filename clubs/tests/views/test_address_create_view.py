"""Tests of the create_address view."""
import datetime

from clubs.models import Address, Club, MeetingAddress, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse
from schedule.models import Calendar, Event, Rule


class CreateEventAddressViewTest(TestCase):
    """Tests of the create_address view."""

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
            'start': datetime.datetime(2008, 11, 5, 15, 0),
            'end': datetime.datetime(2008, 11, 5, 16, 30),
            'end_recurring_period': datetime.datetime(2009, 6, 1, 0, 0),
            'rule': Rule.objects.get(pk=9),
            'calendar': self.calendar
        }
        event = Event(**data)
        event.save()
        self.event = event

        self.data = {
            "name": "City Library",
            "address1": "New Concordia Wharf",
            "address2": "3 Mill St",
            "zip_code": "SE1 2BB",
            "city": "London",
            "country": "GB"
        }
        self.url = reverse(
            'create_address', kwargs={'calendar_slug': self.calendar.slug, 'event_id': self.event.id}
        )

    def test_create_address_url(self):
        self.assertEqual(self.url, f'/event/address/create/newaddress/{self.calendar.slug}/{self.event.id}/')

    def test_create_address_redirects_when_not_logged_in(self):
        address_count_before = Address.objects.count()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        address_count_after = Address.objects.count()
        self.assertEqual(address_count_after, address_count_before)

    def test_get_create_address(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'address_create.html')

    def test_successful_new_event_address(self):
        self.client.login(email=self.user.email, password="Password123")
        address_count_before = Address.objects.count()
        meeting_address_count_before = MeetingAddress.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        address_count_after = Address.objects.count()
        meeting_address_count_after = MeetingAddress.objects.count()
        self.assertEqual(address_count_after, address_count_before + 1)
        self.assertEqual(meeting_address_count_after, meeting_address_count_before + 1)
        new_meeting_address = MeetingAddress.objects.get(event=self.event)
        self.assertEqual(self.data['name'], new_meeting_address.address.name)
        response_url = reverse('full_calendar', kwargs={'calendar_slug': self.calendar.slug})
        self.assertTemplateUsed(response, 'fullcalendar.html')

    def test_unsuccessful_new_address(self):
        self.client.login(email=self.user.email, password="Password123")
        address_count_before = Address.objects.count()
        meeting_address_count_before = MeetingAddress.objects.count()
        self.data['name'] = ""
        response = self.client.post(self.url, self.data, follow=True)
        address_count_after = Address.objects.count()
        meeting_address_count_after = MeetingAddress.objects.count()
        self.assertEqual(address_count_after, address_count_before)
        self.assertEqual(meeting_address_count_after, meeting_address_count_before)
        self.assertTemplateUsed(response, 'address_create.html')
