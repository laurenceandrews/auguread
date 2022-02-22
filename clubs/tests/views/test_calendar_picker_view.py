"""Tests of the calendar picker view."""
from clubs.forms import CalendarPickerForm
from clubs.models import Club, User
from clubs.tests.helpers import LogInTester
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from schedule.models import Calendar, Event, Rule


class CalendarPickerViewTestCase(TestCase, LogInTester):
    """Tests of the calendar picker view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_club.json',
    ]

    def setUp(self):
        self.url = reverse('calendar_picker')
        self.user = User.objects.get(username='@johndoe')
        self.calendar = Calendar.objects.get(pk=5)
        self.club = Club.objects.get(pk=6)
        self.form_input = {
            'calendar': self.calendar
        }

    def test_calendar_picker_url(self):
        self.assertEqual(self.url, '/calendar_picker/')

    def test_get_calendar_picker(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'calendar_picker.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CalendarPickerForm))
        self.assertFalse(form.is_bound)

    def test_unsuccesful_calendar_picker(self):
        self.form_input['calendar'] = 'BAD_CALENDAR'
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'calendar_picker.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CalendarPickerForm))
        self.assertTrue(form.is_bound)

    def test_succesful_calendar_picker(self):
        response = self.client.post(self.url, self.form_input, follow=True)
        expected_page_content = "<h1>You're viewing: " + self.calendar.name + "</h1>"
        self.assertContains(response, expected_page_content)
