"""Tests of the club delete view."""
import datetime

from clubs.models import Club, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse
from schedule.models import Calendar, Event, Rule


class DeleteClubViewTest(TestCase):
    """Tests of the delete_club view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_rules.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_clubs.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self.calendar = Calendar.objects.get(pk=5)
        self.club = Club.objects.get(pk=6)

        self.data = {}

        self.url = reverse(
            'club_delete', kwargs={'club_id': self.club.id}
        )

    def test_delete_club_url(self):
        self.assertEqual(self.url, f'/club/delete/{self.club.id}')

    def test_delete_club_redirects_when_not_logged_in(self):
        club_count_before = Club.objects.count()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        club_count_after = Club.objects.count()
        self.assertEqual(club_count_after, club_count_before)

    def test_delete_club_redirects_when_not_a_club_owner(self):
        calendar_not_owner = Calendar.objects.get(pk=17)
        club_not_owner = Club.objects.get(pk=16)
        form_input = {}
        url = reverse(
            'club_delete', kwargs={'club_id': club_not_owner.id}
        )

        club_count_before = Club.objects.count()
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(url)
        redirect_url = reverse('user_clubs', kwargs={'role_num': 4})
        response = self.client.post(url, form_input, follow=True)
        self.assertTemplateUsed(response, 'summary_clubs_table.html')
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        club_count_after = Club.objects.count()
        self.assertEqual(club_count_after, club_count_before)

    def test_get_delete_club(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_delete.html')
        self.assertEqual(response.context['club'], self.club)

    def test_post_delete_club(self):
        self.client.login(email=self.user.email, password="Password123")
        post_response = self.client.post(self.url, follow=True)
        self.assertTemplateUsed(post_response, 'user_summary.html')
