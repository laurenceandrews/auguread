from django.test import TestCase
from clubs.models import User
from clubs.forms import NewClubForm


class NewClubTestCase(TestCase):

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(email="johndoe@example.org")

    def test_valid_new_club(self):
        input = {'name': 'x'*50, 'location': 'y'*500, 'description': 'z'*520}
        form = NewClubForm(data=input)
        self.assertTrue(form.is_valid())

    def test_form_with_invalid_name(self):
        input = {'name': 'x'*51, 'location': 'y'*500, 'description': 'z'*520}
        form = NewClubForm(data=input)
        self.assertFalse(form.is_valid())

    def test_form_with_invalid_location(self):
        input = {'name': 'x'*50, 'location': 'y'*501, 'description': 'z'*520}
        form = NewClubForm(data=input)
        self.assertFalse(form.is_valid())

    def test_form_with_invalid_description(self):
        input = {'name': 'x'*50, 'location': 'y'*500, 'description': 'z'*521}
        form = NewClubForm(data=input)
        self.assertFalse(form.is_valid())
