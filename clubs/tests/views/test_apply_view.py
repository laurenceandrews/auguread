"""Unit test for the apply view"""
from clubs.models import Club, Club_Users, User
from django.test import TestCase
from django.urls import reverse


class ApplyViewTestCase(TestCase):
    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/default_rules.json',
        'clubs/tests/fixtures/default_book.json',
        'clubs/tests/fixtures/other_books.json',
        'clubs/tests/fixtures/seven_pos_ratings.json'
    ]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.club = Club.objects.get(pk=6)
        self._create_club_owners_and_applicants()
        self.url = reverse('apply', kwargs={'club_id': self.club.id})

    def test_apply_club_if_no_club_user_exists(self):
        self.client.login(email=self.applicant.email, password='Password123')
        club_users_count_before = Club_Users.objects.count()
        self.user = User.objects.get(pk=3)
        response = self.client.get(self.url)
        self.assertTrue(self.applicant in self.club.applicants())
        club_users_count_after = Club_Users.objects.count()
        self.assertTrue(club_users_count_after, club_users_count_before + 1)

    def test_apply_club_if_club_exists(self):
        self.client.login(email=self.applicant.email, password='Password123')
        club_users_count_before = Club_Users.objects.count()
        response = self.client.get(self.url)
        club_users_count_after = Club_Users.objects.count()
        self.assertTrue(club_users_count_after, club_users_count_before)

    def _create_club_owners_and_applicants(self):
        self.club_owner = self.club.owner
        self.applicant = User.objects.get(pk=2)
        self.club.applied_by(self.applicant)
        self.club_applicants = self.club.applicants
