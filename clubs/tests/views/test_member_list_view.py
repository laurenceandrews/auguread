"""Unit tests for the Member list."""
from clubs.models import ApplicantMembership, Club, Club_Users, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse


class MemberListViewTestCase(TestCase):
    """Unit tests for the Member list."""
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

        self.data = {}

        self.url = reverse('member_list', kwargs={'club_id': self.club.id})

    def test_member_list_url(self):
        self.assertEqual(self.url, f'/{self.club.id}/members')

    def test_get_member_list(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'member_list.html')

    def test_member_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )

    # def test_applicant_can_not_access_member_list(self):
    #     self.client.login(email=self.applicant.email, password="Password123")
    #     response = self.client.get(self.url)
    #     redirect_url = reverse('club_list')
    #     self.assertTemplateUsed(response, 'club_list.html')
    #     self.assertRedirects(response, redirect_url,
    #                          status_code=302, target_status_code=200)

    def _create_club_owner_members_and_applicants(self):
        self.club_owner = self.club.owner
        self.applicant = User.objects.get(pk=2)
        self.club.applicants.add(self.applicant)
        self.club_applicants = self.club.applicants.all()
        self.member = User.objects.get(pk=3)
        self.club.members.add(self.member)
        self.club_members = self.club.members.all()
