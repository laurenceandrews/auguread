"""Unit tests of the meeting address form."""
from clubs.forms import MeetingAddressForm
from clubs.models import MeetingAddress, User
from django import forms
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from schedule.models import Calendar, Event, Rule


class MeetingAddressFormTestCase(TestCase):
    """Unit tests of the meeting address form."""

    def setUp(self):
        self.form_input = {
            'name': "City Library",
            'address1': "Palm Street",
            'address2': "Clifton",
            'zip_code': 00000,
            'city': "London",
            'country': "GB"
        }

    def test_valid_meeting_address_form(self):
        form = MeetingAddressForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = MeetingAddressForm()
        self.assertIn('name', form.fields)
        self.assertIn('address1', form.fields)
        self.assertIn('address2', form.fields)
        self.assertIn('zip_code', form.fields)
        self.assertIn('city', form.fields)
        self.assertIn('country', form.fields)
