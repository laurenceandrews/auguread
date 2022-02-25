"""Unit tests for the Applicant list."""
from django.test import TestCase
from clubs.models import Club
from django.urls import reverse


class ApplicantListViewTestCase(TestCase):
    """Unit tests for the Applicant list."""
    fixtures = [
        'clubs/tests/fixtures/club.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.owner = Club.objects.get(id=1).owner
        self.owner = Club.objects.get(id=1).owners.all()[0]
        self.member = Club.objects.get(id=1).members.all()[0]
        self.applicant = Club.objects.get(id=1).applicants.all()[0]
        self.url = reverse('applicant_list', kwargs={'club_id': self.club.id})
        self.approve_url = reverse(
            'approve', kwargs={'club_id': self.club.id, 'user_id': self.applicant.id})

    def test_get_applicant_list(self):
        self.client.login(email=self.owner.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicant_list.html')

    def test_membr_can_not_access_applicant_list(self):
        self.client.login(email=self.member.email, password="Password123")
        response = self.client.get(self.url)
        redirect_url = reverse('club_list')
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)

    def test_post_applicant_list(self):
        self.client.login(email=self.owner.email, password="Password123")
        response = self.client.get(self.approve_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.applicant in self.club.members.all())
        self.assertFalse(self.applicant in self.club.applicants.all())

    def test_applicant_list_url(self):
        self.assertEqual(self.url, '/1/applicants')

    def test_member_can_not_approve_applicant(self):
        self.client.login(email='jeb@example.org', password='Password123')
        self.client.get(self.approve_url)
        self.assertTrue(self.applicant in self.club.applicants.all())
        self.assertFalse(self.applicant in self.club.members.all())

    def test_owner_can_approve_applicant(self):
        self.client.login(email='billie@example.org', password='Password123')
        self.client.get(self.approve_url)
        self.assertTrue(self.applicant in self.club.members.all())
        self.assertFalse(self.applicant in self.club.applicants.all())

    def test_owner_can_not_approve_not_exists_user(self):
        self.client.login(email='billie@example.org', password='Password123')
        url = reverse('approve', kwargs={
                      'club_id': self.club.id, 'user_id': 1000000})
        response = self.client.get(url)
        redirect_url = reverse('applicant_list', kwargs={
                               'club_id': self.club.id})
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)

    def test_accept_applicant_with_in_applicant_list(self):
        self.client.login(email='billie@example.org', password='Password123')
        post_data = {'check[]': ['applicant@example.org']}
        self.client.post(self.url, post_data)
        self.assertTrue(self.applicant in self.club.members.all())
        self.assertFalse(self.applicant in self.club.applicants.all())
