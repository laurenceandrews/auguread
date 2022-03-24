"""Unit test for the delete account view"""
from clubs.forms import UserDeleteForm
from clubs.models import User
from django.conf import settings
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse


class DeleteAccountViewTestCase(TestCase):
    fixtures = [
        'clubs/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        self.url = reverse('delete_account')
        self.user = User.objects.get(email='johndoe@example.org')

    def test_delete_account_url(self):
        self.assertEqual(self.url, '/user/delete/')
