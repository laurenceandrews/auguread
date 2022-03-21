"""Unit test for the apply view"""
from clubs.models import Club, User
from django.test import TestCase
from django.urls import reverse


class ApplyViewTestCase(TestCase):
    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/default_rules.json',
    ]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.club = Club.objects.get(pk=6)
        self._create_club_owner_members_and_applicants()
        self.url = reverse('apply', kwargs={'club_id': self.club.id})

    def test_apply_club(self):
        self.client.login(email=self.applicant.email, password='Password123')
        response = self.client.get(self.url)
        redirect_url = reverse('club_list')
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)
        self.assertTrue(self.applicant in self.club.applicants())

    def _create_club_owner_members_and_applicants(self):
        self.club_owner = self.club.owner
        self.applicant = User.objects.get(pk=2)
        self.club.applied_by(self.applicant)
        self.club_applicants = self.club.applicants
        self.member = User.objects.get(pk=3)
        self.club.applied_by(self.member)
        self.club.accept(self.member)
        self.club_members = self.club.members
