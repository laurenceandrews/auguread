"""Unit test for the enter view"""
from clubs.models import Club, User
from django.conf import settings
from django.test import TestCase
from django.urls import reverse


class EnterViewTestCase(TestCase):
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
        self.url = reverse('enter', kwargs={'club_id': self.club.id})

    def test_enter_club(self):
        self.client.login(email=self.owner.email, password='Password123')
        response = self.client.get(self.url)
        redirect_url = reverse('show_user', kwargs={
                               'club_id': self.club.id, 'user_id': self.owner.id})
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)

    def test_applicant_should_not_be_able_to_enter_club(self):
        self.client.login(email=self.applicant.email, password='Password123')
        response = self.client.get(self.url)
        redirect_url = reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)

    def _create_club_owner_members_and_applicants(self):
        self.owner = self.club.owner
        self.applicant = User.objects.get(pk=2)
        self.club.applicants.add(self.applicant)
        self.club_applicants = self.club.applicants.all()
        self.member = User.objects.get(pk=3)
        self.club.members.add(self.member)
        self.club_members = self.club.members.all()
