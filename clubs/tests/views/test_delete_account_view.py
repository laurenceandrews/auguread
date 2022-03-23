"""Unit test for the delete account view"""
from clubs.models import User
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.contrib import messages

class DeleteAccountViewTestCase(TestCase):
    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/default_rules.json',
    ]

    def setUp(self):
        self.url = reverse('delete_account')
        self.user = User.objects.get(email='johndoe@example.org')

    def test_delete_account_url(self):
        self.assertEqual(self.url, '/delete_account/')
