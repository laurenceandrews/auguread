"""Unit tests for the Member list."""
from django.test import TestCase
from clubs.models import Club
from django.urls import reverse


class MemberListViewTestCase(TestCase):
    """Unit tests for the Member list."""
    fixtures = [
        'clubs/tests/fixtures/club.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.owner = Club.objects.get(id=1).owner
        self.owner = Club.objects.get(id=1).owners.all()[0]
        self.member = Club.objects.get(id=1).members.all()[0]
        self.applicant = Club.objects.get(id=1).applicants.all()[0]
        self.url = reverse('member_list', kwargs={'club_id': self.club.id})
        self.promote_url = reverse(
            'promote', kwargs={'club_id': self.club.id, 'user_id': self.member.id})

    def test_member_list_url(self):
        self.assertEqual(self.url, '/1/members')

    def test_get_member_list(self):
        self.client.login(email=self.officer.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'member_list.html')

    def test_applicant_can_not_access_member_list(self):
        self.client.login(email=self.applicant.email, password="Password123")
        response = self.client.get(self.url)
        redirect_url = reverse('club_list')
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)

    def test_officer_can_not_promote_member(self):
        self.client.login(email='val@example.org', password='Password123')
        self.client.get(self.promote_url)
        self.assertFalse(self.member in self.club.officers.all())
        self.assertTrue(self.member in self.club.members.all())

    def test_owner_can_promote_member(self):
        self.client.login(email='billie@example.org', password='Password123')
        self.client.get(self.promote_url)
        self.assertTrue(self.member in self.club.officers.all())
        self.assertFalse(self.member in self.club.members.all())

    def test_owner_can_not_promote_not_exists_user(self):
        self.client.login(email='billie@example.org', password='Password123')
        promote_url = reverse(
            'promote', kwargs={'club_id': self.club.id, 'user_id': 100000})
        response = self.client.get(promote_url)
        redirect_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)

    def test_promote_member_with_in_member_list(self):
        self.client.login(email='billie@example.org',
                          password='Password123')
        post_email = self.member.email
        post_data = {'check[]': [post_email]}
        self.client.post(self.url, post_data)
        self.assertTrue(self.member in self.club.officers.all())
        self.assertFalse(self.member in self.club.members.all())
