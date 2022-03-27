from clubs.forms import ClubUpdateForm
from clubs.models import User
from django.test import TestCase
from schedule.models import Calendar, Event, Rule


class ClubUpdateFormTestCase(TestCase):

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_calendar.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.calendar = Calendar.objects.get(pk=5)

        self.form_input = {
            "name": "Pink Club",
            "description": "A club that reads lots of pink books.",
            "meeting_type": "ONL"
        }

    def test_valid_new_club(self):
        form = ClubUpdateForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = ClubUpdateForm()
        self.assertIn('name', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('meeting_type', form.fields)

    def test_name_cannot_exceed_50_characters(self):
        self.form_input['name'] = 'x' * 51
        form = ClubUpdateForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_name_cannot_be_blank(self):
        self.form_input['name'] = ''
        form = ClubUpdateForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_description_cannot_exceed_520_characters(self):
        self.form_input['description'] = 'z' * 521
        form = ClubUpdateForm(data=self.form_input)
        self.assertFalse(form.is_valid())
