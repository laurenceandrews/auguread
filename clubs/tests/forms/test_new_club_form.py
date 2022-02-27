from clubs.forms import NewClubForm
from clubs.models import User
from django.test import TestCase
from schedule.models import Calendar, Event, Rule


class NewClubTestCase(TestCase):

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_calendar.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(email="johndoe@example.org")
        self.existid_calendar = Calendar.objects.get(pk=5)
        self.form_input = {
            'name': 'Fun Reading Club',
            'location': 'London, GB',
            'description': 'A book club that is fun.',
            'avg_reading_speed': 200,
            'calendar_name': 'Fun Reading Clubs Calendar'
        }

    def test_valid_new_club(self):
        form = NewClubForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = NewClubForm()
        self.assertIn('name', form.fields)
        self.assertIn('location', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('avg_reading_speed', form.fields)
        self.assertIn('calendar_name', form.fields)

    def test_name_cannot_exceed_50_characters(self):
        self.form_input['name'] = 'x' * 51
        form = NewClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_location_cannot_exceed_500_characters(self):
        self.form_input['location'] = 'y' * 501
        form = NewClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_description_cannot_exceed_520_characters(self):
        self.form_input['location'] = 'z' * 521
        form = NewClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_calendar_name_must_be_unique(self):
        self.form_input['calendar_name'] = "Fun Club's Calendar"
        form = NewClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())
