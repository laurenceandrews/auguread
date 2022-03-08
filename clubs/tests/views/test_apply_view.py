"""Unit test for the apply view"""
from django.test import TestCase
from clubs.models import Club, User
from django.urls import reverse


class ApplyViewTestCase(TestCase):
    fixtures = [
        'clubs/tests/fixtures/club.json',
        'clubs/tests/fixtures/applicant_user.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.applicant = User.objects.get(id=4)
        self.url = reverse('apply', kwargs={'club_id': self.club.id})

    def test_apply_club(self):
        self.client.login(email=self.applicant.email, password='Password123')
        response = self.client.get(self.url)
        redirect_url = reverse('club_list')
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)
        self.assertTrue(self.applicant in self.club.applicants.all())
