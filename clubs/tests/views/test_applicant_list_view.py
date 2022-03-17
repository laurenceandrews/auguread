"""Unit tests for the Applicant list."""
from clubs.models import Club, User
from django.test import TestCase
from django.urls import reverse

"""WILL BE UPDATED"""


class ApplicantListViewTestCase(TestCase):
    """Unit tests for the Applicant list."""
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
        self.club = Club.objects.get(pk=19)
        self._create_club_owner_members_and_applicants()
        self.url = reverse('applicant_list', kwargs={'club_id': self.club.id})
        self.approve_url = reverse(
            'approve', kwargs={'club_id': self.club.id, 'user_id': self.applicant.id})

    def test_applicant_list_url(self):
        self.assertEqual(self.url, f'/{self.club.id}/applicants')

    def test_get_applicant_list(self):
        self.client.login(email=self.owner.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicant_list.html')

    # def test_member_can_not_access_applicant_list(self):
    #     self.client.login(email=self.member.email, password="Password123")
    #     response = self.client.get(self.url)
    #     redirect_url = reverse('club_list')
    #     self.assertRedirects(response, redirect_url,
    #                          status_code=302, target_status_code=200)

    def test_post_applicant_list(self):
        self.client.login(email=self.owner.email, password="Password123")
        response = self.client.get(self.approve_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.applicant in self.club.members.all())
        self.assertFalse(self.applicant in self.club.applicants.all())

    def test_member_can_not_approve_applicant(self):
        self.client.login(email=self.member.email, password="Password123")
        self.client.get(self.approve_url)
        # print(self.club_applicants)
        # print(self.club_members)
        self.assertTrue(self.applicant in self.club.applicants.all())
        self.assertFalse(self.applicant in self.club.members.all())

    def test_owner_can_approve_applicant(self):
        self.client.login(email=self.owner.email, password="Password123")
        self.client.get(self.approve_url)
        self.assertTrue(self.applicant in self.club.members.all())
        self.assertFalse(self.applicant in self.club.applicants.all())

    def test_owner_can_not_approve_not_exists_user(self):
        self.client.login(email=self.owner.email, password="Password123")
        url = reverse('approve', kwargs={
                      'club_id': self.club.id, 'user_id': 1000000})
        response = self.client.get(url)
        redirect_url = reverse('applicant_list', kwargs={
                               'club_id': self.club.id})
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)

    def test_accept_applicant_with_in_applicant_list(self):
        self.client.login(email=self.owner.email, password="Password123")
        post_data = {'check[]': [self.applicant.email]}
        self.client.post(self.url, post_data)
        self.assertTrue(self.applicant in self.club.members.all())
        self.assertFalse(self.applicant in self.club.applicants.all())

    def _create_club_owner_members_and_applicants(self):
        self.owner = self.club.owner
        self.applicant = User.objects.get(pk=2)
        self.club.applicants.add(self.applicant)
        self.club_applicants = self.club.applicants.all()
        self.member = User.objects.get(pk=3)
        self.club.members.add(self.member)
        self.club_members = self.club.members.all()
        self.club.save()
