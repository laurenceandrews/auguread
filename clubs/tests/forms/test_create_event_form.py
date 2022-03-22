import datetime

from clubs.forms import CreateEventForm
from clubs.models import Club, User
from django.test import TestCase
from schedule.models import Calendar, Event, Rule


class CreateEventFormTestCase(TestCase):

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_rules.json',
        'clubs/tests/fixtures/default_club.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(email="johndoe@example.org")
        self.calendar = Calendar.objects.get(pk=5)
        self.club = Club.objects.get(pk=6)
        self.data = {
            'title': 'Exercise',
            'start': datetime.datetime(2008, 11, 3, 8, 0),
            'end': datetime.datetime(2008, 11, 3, 9, 0),
            'end_recurring_period': datetime.datetime(2009, 6, 1, 0, 0),
            'rule': Rule.objects.get(pk=9),
            'calendar': self.calendar
        }
        self.existing_event = Event(**self.data)
        self.existing_event.save()
        self.form_input = {
            'title': 'Exercise'
        }

    # def test_valid_new_event(self):
    #     form = CreateEventForm(data=self.form_input)
    #     self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = CreateEventForm()
        self.assertIn('title', form.fields)
        self.assertIn('start', form.fields)
        self.assertIn('end', form.fields)

    def test_end_must_be_later_than_start(self):
        self.form_input['start'] = self.data['end']
        form = CreateEventForm(data=self.form_input)
        self.assertFalse(form.is_valid())
