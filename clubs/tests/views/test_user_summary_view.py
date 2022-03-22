"""Tests of the user summary view."""
from clubs.models import User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse


class UserSummaryViewTestCase(TestCase):
    """Tests of the user summary view."""

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('user_summary')
        self.user = User.objects.get(email='johndoe@example.org')

    def test_user_summary_url(self):
        self.assertEqual(self.url, '/summary/')

    def test_get_user_summary(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_summary.html')

    def test_get_user_summary_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_user_summary_has_required_nav_bar_options(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_summary.html')
        self.assertContains(response, '<option>Clubs with application pending</option>', status_code=200)
        self.assertContains(response, '<option>Clubs with membership</option>', status_code=200)
        self.assertContains(response, '<option>Clubs with ownership</option>', status_code=200)
        self.assertContains(response, '<option>My clubs currently reading</option>', status_code=200)
        self.assertContains(response, '<option>My favourite books</option>', status_code=200)
        self.assertContains(response, '<option>My current book</option>', status_code=200)
