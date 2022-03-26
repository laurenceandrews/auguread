from clubs.forms import NewClubForm
from clubs.models import Club, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse


class NewClubTest(TestCase):

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(email='johndoe@example.org')
        self.url = reverse('new_club')
        self.club_city = 'London'
        self.club_country = 'GB'
        self.club_location = self.club_city + ", " + self.club_country
        self.data = {
            'name': 'Fun Reading Club',
            'city': self.club_city,
            'country': self.club_country,
            'description': 'A book club that is fun.',
            'calendar_name': 'Fun Reading Clubs Calendar',
            'meeting_type': 'ONL'
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
        self.client.login(email=self.user.email, password="Password123")
        clubs_count_before = Club.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        clubs_count_after = Club.objects.count()
        self.assertEqual(clubs_count_after, clubs_count_before + 1)
        new_club = Club.objects.get(name=self.data['name'])
        self.assertEqual(self.data['name'], new_club.name)
        self.assertEqual(self.club_location, new_club.location)
        self.assertEqual(self.data['description'], new_club.description)
        self.assertEqual(self.data['calendar_name'], new_club.calendar.name)
        self.assertEqual(self.data['meeting_type'], new_club.meeting_type)
        response_url = reverse('club_detail', kwargs={'club_id': new_club.id})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'club_detail.html')

    def test_unsuccessful_new_club(self):
        self.client.login(email=self.user.email, password='Password123')
        clubs_count_before = Club.objects.count()
        self.data['name'] = ""
        response = self.client.post(self.url, self.data, follow=True)
        clubs_count_after = Club.objects.count()
        self.assertEqual(clubs_count_after, clubs_count_before)
        self.assertTemplateUsed(response, 'new_club.html')

    def test_unsuccessful_new_club_creation_with_blank_name(self):
        self.client.login(email="johndoe@example.org",
                          password='Password123')
        club_count_before = Club.objects.count()
        self.data['name'] = ""
        response = self.client.post(self.url, self.data, follow=True)
        club_count_after = Club.objects.count()
        self.assertEqual(club_count_after, club_count_before)
        self.assertTemplateUsed(response, 'new_club.html')

    def test_unsuccessful_new_club_creation_with_blank_calendar_name(self):
        self.client.login(email="johndoe@example.org",
                          password='Password123')
        club_count_before = Club.objects.count()
        self.data['calendar_name'] = ""
        response = self.client.post(self.url, self.data, follow=True)
        club_count_after = Club.objects.count()
        self.assertEqual(club_count_after, club_count_before)
        self.assertTemplateUsed(response, 'new_club.html')

    def test_unsuccessful_new_club_creation_with_blank_description(self):
        self.client.login(email="johndoe@example.org",
                          password='Password123')
        club_count_before = Club.objects.count()
        self.data['description'] = ""
        response = self.client.post(self.url, self.data, follow=True)
        club_count_after = Club.objects.count()
        self.assertEqual(club_count_after, club_count_before)
        self.assertTemplateUsed(response, 'new_club.html')

    def test_cannot_create_club_for_other_user(self):
        self.client.login(email="johndoe@example.org",
                          password='Password123')
        other_user = User.objects.get(email="janedoe@example.org",)
        self.data['owner'] = other_user.id
        club_count_before = Club.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        club_count_after = Club.objects.count()
        new_club = Club.objects.get(id=Club.objects.count())
        self.assertEqual(club_count_after, club_count_before + 1)
        self.assertEqual(self.user, new_club.owner)
