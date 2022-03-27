"""Unit tests for the user detail."""
from clubs.models import Club, User
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from schedule.models import Calendar, Event, Rule


class UserDetailViewTestCase(TestCase):
    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.current_user = User.objects.get(pk=1)
        self.user = User.objects.get(pk=2)
        self.url = reverse('user_detail', kwargs={'user_id': self.user.id})

    def test_user_detail_for_current_user(self):
        self.client.login(email=self.current_user.email, password="Password123")
        url = reverse('user_detail', kwargs={'user_id': self.current_user.id})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_detail.html')

    def test_user_detail_for_other_users(self):
        self.client.login(email=self.current_user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_detail.html')

    def test_user_detail_with_invalid_user_id(self):
        self.client.login(email=self.user.email, password="Password123")
        url = reverse('user_detail', kwargs={'user_id': 0})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
