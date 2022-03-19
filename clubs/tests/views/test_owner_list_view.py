"""Unit tests for the Owner list."""
from django.test import TestCase
from clubs.models import Club, User
from django.urls import reverse


# class OwnerModelTestCase(TestCase):
#     """Unit tests for the Owner list."""
#     fixtures = [
#         'clubs/tests/fixtures/default_user.json',
#         'clubs/tests/fixtures/other_users.json',
#         'clubs/tests/fixtures/default_calendar.json',
#         'clubs/tests/fixtures/default_club.json',
#         'clubs/tests/fixtures/detailed_club.json',
#         'clubs/tests/fixtures/default_rules.json',
#     ]
#     def setUp(self):
#         self.user = User.objects.get(pk=1)
#         self.club = Club.objects.get(pk=19)
#         self.owner = Club.objects.get(pk=19).owner
#         self.member = Club.objects.get(pk=19).members.all()
#         self.applicant = Club.objects.get(pk=19).applicants.all()
#         self.url = reverse('owner_list', kwargs={'club_id': self.club.id})
#         self.approve_url = reverse(
#             'approve', kwargs={'club_id': self.club.id, 'user_id': self.applicant.id})
#
#     def test_user_list_url(self):
#         self.assertEqual(self.url, f'/{self.club.id}/owners')
#
#     def test_get_owner_list(self):
#         self.client.login(email=self.owner.email, password="Password123")
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'owner_list.html')
#
#     def test_officers_can_not_access_owner_list(self):
#         self.client.login(email=self.owner.email, password="Password123")
#         response = self.client.get(self.url)
#         redirect_url = reverse('club_list')
#         self.assertRedirects(response, redirect_url,
#                              status_code=302, target_status_code=200)
#
#     def test_owner_can_transer_ownership_to_officer(self):
#         self.client.login(email='johndoe@example.org', password='Password123')
#         self.assertTrue(self.club.owner == self.owner)
#         transfer_url = reverse('transfer', kwargs={
#                                'club_id': self.club.id, 'user_id': self.officer.id})
#         self.client.get(transfer_url)
#         self.assertTrue(self.club.owner in self.club.owners.all())
#         self.assertTrue(Club.objects.get(id=1).owner == self.owner)
#
#     def test_owner_can_transfer_ownership_to_not_exists_owners(self):
#         self.client.login(email='johndoe@example.org', password='Password123')
#         self.assertTrue(self.club.owner == self.owner)
#         self.assertTrue(self.owner in self.club.owners.all())
#         transfer_url = reverse('transfer', kwargs={
#                                'club_id': self.club.id, 'user_id': 10000000000})
#         response = self.client.get(transfer_url)
#         redirect_url = reverse('officer_list', kwargs={
#                                'club_id': self.club.id})
#         self.assertRedirects(response, redirect_url,
#                              status_code=302, target_status_code=200)
#
#     def test_owner_cannot_transfer_ownership_to_member(self):
#         self.client.login(email='johndoe@example.org', password='Password123')
#         self.assertTrue(self.owner in self.club.owners.all())
#         transfer_url = reverse('transfer', kwargs={
#                                'club_id': self.club.id, 'user_id': self.member.id})
#         self.client.get(transfer_url)
#         self.assertTrue(self.club.owner == self.owner)
#         self.assertTrue(self.owner in self.club.owners.all())
