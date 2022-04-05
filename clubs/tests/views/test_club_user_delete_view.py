"""Tests of the club_user_event view."""
import datetime

from clubs.models import Club, Club_Users, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse
from schedule.models import Calendar, Event, Rule


class DeleteClubUsersViewTest(TestCase):
    """Tests of the delete_club_user view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_rules.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_clubs.json',
        'clubs/tests/fixtures/default_book.json',
        'clubs/tests/fixtures/other_books.json',
        'clubs/tests/fixtures/seven_pos_ratings.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self.club = Club.objects.get(pk=26)
        self.club_user = Club_Users.objects.create(user=self.user, club=self.club, role_num='1')

        self.data = {}

        self.url = reverse(
            'delete_club_user', kwargs={'club_users_id': self.club_user.id}
        )

    def test_delete_club_user_url(self):
        self.assertEqual(self.url, f'/club/user/delete/{self.club_user.id}/')

    def test_delete_club_user_redirects_when_not_logged_in(self):
        club_users_count_before = Club_Users.objects.count()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        club_users_count_after = Club_Users.objects.count()
        self.assertEqual(club_users_count_after, club_users_count_before)

    def test_get_delete_club_user_with_role_num_1(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_user_delete.html')
        self.assertEqual(response.context['club_users'], self.club_user)

    def test_get_delete_club_user_with_role_num_2(self):
        self.client.login(email=self.user.email, password="Password123")
        user = User.objects.get(username='@janedoe')
        club_user = Club_Users.objects.create(user=user, club=self.club, role_num='2')
        url = reverse(
            'delete_club_user', kwargs={'club_users_id': club_user.id}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_user_delete.html')
        self.assertEqual(response.context['club_users'], club_user)

    def test_get_delete_club_user_with_role_num_4(self):
        self.client.login(email=self.user.email, password="Password123")
        user = User.objects.get(username='@janedoe')
        club_user = Club_Users.objects.create(user=user, club=self.club, role_num='4')
        url = reverse(
            'delete_club_user', kwargs={'club_users_id': club_user.id}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_user_delete.html')
        self.assertEqual(response.context['club_users'], club_user)

    def test_post_delete_club_user(self):
        self.client.login(email=self.user.email, password="Password123")
        post_response = self.client.post(self.url, follow=True)
        self.assertTemplateUsed(post_response, 'club_detail.html')
