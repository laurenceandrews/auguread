from clubs.models import Club
from django.test import TestCase
from django.urls import reverse
from schedule.models import Calendar, Event, Rule


class EventsListTest(TestCase):

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_club.json',
    ]

    def setUp(self):
        self.url = reverse('club_list')
        self.user = User.objects.get(username='johndoe')
        self.club_names = ["Yellow", "Blue", "Green", "Red"]

    def test_club_list_url(self):
        self.assertEqual(self.url, '/clubs/')

    def test_get_club_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_clubs()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_list.html')
        self.assertEqual(len(response.context['clubs']), 4)
        for club_name in self.club_names:
            club = Club.objects.get(name=club_name)
            self.assertContains(response, club.name)
            club_url = reverse('show_club', kwargs={'club_id': club.id})
            self.assertContains(response, club_url)

    def test_get_club_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def _create_test_clubs(self):
        for club_name in self.club_names:
            Club.objects.create(name=club_name,
                                location=f'{club_name} Town',
                                description=f'A club named {club_name}')
