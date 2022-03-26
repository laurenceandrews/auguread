"""Tests of the user delete view."""
import datetime

from clubs.models import Club, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse
from schedule.models import Calendar, Event, Rule


class DeleteUserViewTest(TestCase):
    """Tests of the delete_account view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_rules.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_clubs.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self.calendar = Calendar.objects.get(pk=5)
        self.club = Club.objects.get(pk=6)

        self.data = {}

        self.url = reverse(
            'delete_account'
        )

    def test_delete_account_url(self):
        self.assertEqual(self.url, '/user/delete/')

    def test_delete_account_redirects_when_not_logged_in(self):
        user_count_before = User.objects.count()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        user_count_after = User.objects.count()
        self.assertEqual(user_count_after, user_count_before)

    def test_get_delete_account(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'delete_account.html')
        self.assertEqual(response.context['user'], self.user)

    def test_post_delete_account(self):
        self.client.login(email=self.user.email, password="Password123")
        post_response = self.client.post(self.url, follow=True)
        self.assertTemplateUsed(post_response, 'home.html')
