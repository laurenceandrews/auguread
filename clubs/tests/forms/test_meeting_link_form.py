"""Unit tests of the meeting address form."""
from clubs.forms import MeetingLinkForm
from clubs.models import User
from django.test import TestCase
from schedule.models import Calendar, Event, Rule


class MeetingLinkFormTestCase(TestCase):
    """Unit tests of the meeting address form."""

    def setUp(self):
        self.form_input = {
            'meeting_link': "https://www.bing.com/"
        }

    def test_valid_meeting_link_form(self):
        form = MeetingLinkForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = MeetingLinkForm()
        self.assertIn('meeting_link', form.fields)
