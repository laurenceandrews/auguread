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
        self.existing_calendar = Calendar.objects.get(pk=5)
        self.club_city = 'London'
        self.club_country = 'GB'
        self.club_location = self.club_city + ", " + self.club_country
        self.form_input = {
            'name': 'Fun Reading Club',
            'city': self.club_city,
            'country': self.club_country,
            'description': 'A book club that is fun.',
            'avg_reading_speed': 200,
            # 'meeting_type': 'online',
            'calendar_name': 'Fun Reading Clubs Calendar'
        }

    def test_valid_new_club(self):
        self.form_input = {'name': 'x'*50,
                # 'city': self.club_city,
                # 'country': self.club_country,
                'description': 'y'*200,
                'avg_reading_speed': 200,
                # 'calendar_name': 'c'*200,
                'meeting_type': 'z'*50
        }
        form = NewClubForm(data=self.form_input)
        self.assertTrue(form.is_valid())


    def test_form_has_necessary_fields(self):
        form = NewClubForm()
        self.assertIn('name', form.fields)
        self.assertIn('city', form.fields)
        self.assertIn('country', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('avg_reading_speed', form.fields)
        # self.assertIn('meeting_type', form.fields)
        self.assertIn('calendar_name', form.fields)

    def test_name_cannot_exceed_50_characters(self):
        self.form_input['name'] = 'x' * 51
        form = NewClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_city_cannot_exceed_250_characters(self):
        self.form_input['name'] = 'y' * 251
        form = NewClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_description_cannot_exceed_520_characters(self):
        self.form_input['description'] = 'z' * 521
        form = NewClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_calendar_name_must_be_unique(self):
        self.form_input['calendar_name'] = "Fun Club's Calendar"
        form = NewClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())
