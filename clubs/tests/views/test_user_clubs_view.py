"""Tests of the user current book view."""
from clubs.models import Club, Club_Users, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse


class UseCurrentBookViewTestCase(TestCase):
    """Tests of the user current book view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_clubs.json',
        'clubs/tests/fixtures/detailed_club.json',
        'clubs/tests/fixtures/default_rules.json',
    ]

    def setUp(self):
        self.role_num = 1
        self.url = reverse('user_clubs', kwargs={'role_num': self.role_num})
        self.user = User.objects.get(email='johndoe@example.org')
        self._create_clubs_as_owner_member_applicant_and_none()

    def test_user_current_book_url(self):
        url = reverse('user_clubs', kwargs={'role_num': self.role_num})
        self.assertEqual(url, f'/summary/clubs/{self.role_num}')

    def test_get_user_clubs_with_role_num_1(self):
        role_num = 1
        url = reverse('user_clubs', kwargs={'role_num': role_num})
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/clubs_table.html')
        self.assertEqual(len(response.context['clubs']), 1)

    def test_get_user_clubs_with_role_num_2(self):
        role_num = 2
        url = reverse('user_clubs', kwargs={'role_num': role_num})
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/clubs_table.html')
        self.assertEqual(len(response.context['clubs']), 1)

    def test_get_user_clubs_with_role_num_3(self):
        role_num = 3
        url = reverse('user_clubs', kwargs={'role_num': role_num})
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/clubs_table.html')
        self.assertContains(response, '<p>No clubs to show.</p>', status_code=200)

    def test_get_user_clubs__with_role_num_4(self):
        role_num = 4
        url = reverse('user_clubs', kwargs={'role_num': role_num})
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/clubs_table.html')
        self.assertEqual(len(response.context['clubs']), 2)

    def test_get_user_clubs_with_invalid_role_num(self):
        role_num = 5
        url = reverse('user_clubs', kwargs={'role_num': role_num})
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/clubs_table.html')
        self.assertContains(response, '<p>No clubs to show.</p>', status_code=200)

    def test_get_user_clubs_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def _create_clubs_as_owner_member_applicant_and_none(self):
        self.first_club_as_owner = Club.objects.get(pk=6)
        self.club_as_owner = Club.objects.get(pk=12)

        self.club_as_member = Club.objects.get(pk=16)
        Club_Users.objects.create(user=self.user, club=self.club_as_member, role_num="2")

        self.club_as_applicant = Club.objects.get(pk=19)
        self.club_as_applicant.applied_by(self.user)
        Club_Users.objects.create(user=self.user, club=self.club_as_applicant, role_num="1")

        self.club_as_none = Club.objects.get(pk=26)
