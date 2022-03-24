"""Unit tests for the Owner list."""
from django.test import TestCase
from clubs.models import Club, User, Club_Users
from django.urls import reverse
from clubs.tests.helpers import reverse_with_next

class OwnerListViewTestCase(TestCase):
    """Unit tests for the Owner list."""
    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/detailed_club.json',
        'clubs/tests/fixtures/default_rules.json',
    ]
    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.club = Club.objects.get(pk=6)
        self._create_club_owner_members_and_applicants()
        self.data = {}
        self.url = reverse('owner_list', kwargs={'club_id': self.club.id})
        self.approve_url = reverse(
            'approve', kwargs={'club_id': self.club.id, 'user_id': self.applicant.id})


    def test_user_list_url(self):
        self.assertEqual(self.url, f'/{self.club.id}/owners')

    def test_get_owner_list(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'owner_list.html')

    def test_can_transfer_ownership_to_member(self):
        self.club.transfer(self.member)
        self.assertEqual(self.club.owner, self.member)

    # def test_owner_can_transfer_ownership_to_not_exists_member(self):
    #     self.client.login(email='johndoe@example.org', password='Password123')
    #     self.assertTrue(self.club.owner == self.owner)
    #     transfer_url = reverse('transfer', kwargs={
    #                            'club_id': self.club.id, 'user_id': 10000000000})
    #     response = self.client.get(transfer_url)
    #     redirect_url = reverse('owner_list', kwargs={
    #                            'club_id': self.club.id})
    #     self.assertRedirects(response, redirect_url,
    #                          status_code=302, target_status_code=200)

    def test_can_not_transfer_ownership_to_applicant(self):
        self.club.transfer(self.applicant)
        self.assertNotEqual(self.club.owner, self.applicant)

    def _create_club_owner_members_and_applicants(self):
        self.club_owner = self.club.owner
        self.applicant = User.objects.get(pk=2)
        self.club.applied_by(self.applicant)
        self.club_applicants = self.club.applicants
        self.member = User.objects.get(pk=3)
        self.club.applied_by(self.member)
        self.club.accept(self.member)
        self.club_members = self.club.members
