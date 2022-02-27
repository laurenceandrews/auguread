from clubs.forms import NewClubForm
from clubs.models import Club, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse


class NewClubTest(TestCase):

    fixtures = [
        'clubs/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('new_club')
        self.data = {
            'name': 'Fun Reading Club',
            'location': 'London, GB',
            'description': 'A book club that is fun.',
            'avg_reading_speed': 200,
            'calendar_name': 'Fun Reading Clubs Calendar'
        }

    def test_new_club_url(self):
        self.assertEqual(self.url, '/new_club/')

    def test_post_new_club_redirects_when_not_logged_in(self):
        clubs_count_before = Club.objects.count()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        clubs_count_after = Club.objects.count()
        self.assertEqual(clubs_count_after, clubs_count_before)

    def test_successful_new_club(self):
        self.client.login(username=self.user.email, password="Password123")
        clubs_count_before = Club.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        clubs_count_after = Club.objects.count()
        self.assertEqual(clubs_count_after, clubs_count_before + 1)
        new_club = Club.objects.get(name=self.data['name'])
        self.assertEqual(self.data['name'], new_club.name)
        self.assertEqual(self.data['location'], new_club.location)
        self.assertEqual(self.data['description'], new_club.description)
        self.assertEqual(self.data['avg_reading_speed'], new_club.avg_reading_speed)
        self.assertEqual(self.data['calendar_name'], new_club.calendar.name)
        response_url = reverse('club_list')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'club_list.html')

    def test_unsuccessful_new_club(self):
        self.client.login(username=self.user.email, password='Password123')
        clubs_count_before = Club.objects.count()
        self.data['name'] = ""
        response = self.client.post(self.url, self.data, follow=True)
        clubs_count_after = Club.objects.count()
        self.assertEqual(clubs_count_after, clubs_count_before)
        self.assertTemplateUsed(response, 'new_club.html')
