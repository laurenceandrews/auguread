"""Unit tests for the user detail."""
from django.test import TestCase
from clubs.models import Club
from django.urls import reverse


class UserDetailViewTestCase(TestCase):
    fixtures = [
        'clubs/tests/fixtures/club.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.user = Club.objects.get(id=1).owner
        self.url = reverse('user_detail')

    def test_user_detail(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_detail.html')
