"""Tests of the club_detail view."""


from clubs.models import Club, Club_Users, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse
from schedule.models import Calendar, Event, Rule


class ClubDetailViewTest(TestCase):
    """Tests of the club_detail view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_clubs.json',
        'clubs/tests/fixtures/default_rules.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self._create_club_users()

        self.url = reverse(
            'club_detail', kwargs={'club_id': self.club.id}
        )

    def test_book_detail_url(self):
        self.assertEqual(self.url, f'/club/detail/{self.club.id}/')

    def test_get_book_detail_with_valid_id(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_detail.html')
        club = response.context['club']
        self.assertEquals(club, self.club)

    def test_get_book_detail_with_invalid_id(self):
        self.client.login(email=self.user.email, password="Password123")
        url = reverse('club_detail', kwargs={'club_id': 0})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_get_book_detail_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def _create_club_users(self):
        self.club = Club.objects.get(pk=6)

        self.club_as_member = Club.objects.get(pk=16)
        Club_Users.objects.create(user=self.user, club=self.club_as_member, role_num="2")

        self.club_as_applicant = Club.objects.get(pk=26)
        Club_Users.objects.create(user=self.user, club=self.club_as_applicant, role_num="1")
