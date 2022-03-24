"""Unit tests for the user detail."""
from clubs.models import Club
from django.test import TestCase
from django.urls import reverse
from schedule.models import Calendar, Event, Rule


class UserDetailViewTestCase(TestCase):
    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(id=6)
        self.user = Club.objects.get(id=6).owner
        self.url = reverse('user_detail', kwargs={'user_id': self.user.id})

    def test_user_detail(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_detail.html')
