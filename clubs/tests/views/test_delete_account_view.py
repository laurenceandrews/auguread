"""Unit test for the delete account view"""
from clubs.models import User
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.contrib import messages
from clubs.forms import UserDeleteForm

class DeleteAccountViewTestCase(TestCase):
    fixtures = [
        'clubs/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        self.url = reverse('delete_account')
        self.user = User.objects.get(email='johndoe@example.org')

    def test_delete_account_url(self):
        self.assertEqual(self.url, '/delete_account/')
