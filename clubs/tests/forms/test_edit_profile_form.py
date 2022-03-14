"""Unit tests of the user form."""
from django import forms
from django.test import TestCase
from clubs.forms import EditProfileForm
from clubs.models import User

class UserFormTestCase(TestCase):
    """Unit tests of the user form."""

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):

        self.user = User.objects.get(email='johndoe@example.org')
        self.form_input = {
            'first_name': 'John2',
            'last_name': 'Doe',
            'email': 'johndoe2@example.org',
            'public_bio': 'My bio',

        }

    def test_form_has_necessary_fields(self):
        form = EditProfileForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('email', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.CharField))
        self.assertIn('public_bio', form.fields)

    def test_valid_user_form(self):
        form = EditProfileForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        self.form_input['email'] = 'bademail'
        form = EditProfileForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        user = User.objects.get(email='johndoe@example.org')
        form = EditProfileForm(instance=user, data=self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(user.first_name, 'John2')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'johndoe2@example.org')
