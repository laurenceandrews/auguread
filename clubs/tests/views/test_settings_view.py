"""Tests of the settings view."""
from clubs.models import User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse


class SettingsViewTestCase(TestCase):
    """Tests of the settings view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/default_book.json',
        'clubs/tests/fixtures/default_rating.json',
        'clubs/tests/fixtures/default_club_book.json',
        'clubs/tests/fixtures/default_club_user.json',
        'clubs/tests/fixtures/other_books.json',
        'clubs/tests/fixtures/seven_pos_ratings.json'
    ]

    def setUp(self):
        self.url = reverse('settings')
        self.user = User.objects.get(email='johndoe@example.org')

    def test_settings_url(self):
        self.assertEqual(self.url, '/user/settings/')

    def test_get_settings(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings.html')

    def test_get_settings_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
