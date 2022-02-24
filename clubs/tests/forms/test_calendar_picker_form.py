"""Unit tests of the calendar picker form."""
from clubs.forms import CalendarPickerForm
from clubs.models import Club, User
from django import forms
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from schedule.models import Calendar, Event, Rule


class CalendarPickerFormTestCase(TestCase):
    """Unit tests of calendar picker form."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_club.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.calendar = Calendar.objects.get(pk=5)
        self.club = Club.objects.get(pk=6)
        self.form_input = {
            'calendar': self.calendar
        }

    def test_valid_calendar_picker_form(self):
        form = CalendarPickerForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = CalendarPickerForm()
        self.assertIn('calendar', form.fields)
