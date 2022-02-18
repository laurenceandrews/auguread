from django.test import TestCase
from django.urls import reverse
from clubs.models import Club, User
from clubs.forms import NewClubForm


class NewClubTest(TestCase):

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(email='johndoe@example.org')
        self.url = reverse('new_club')
        self.data = {
            'name': "John's club",
            'location': 'here',
            'description': 'smart book club'
        }

    def test_new_club_url(self):
        self.assertEqual(self.url, '/new_club/')

    def test_get_new_club(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, NewClubForm))
        self.assertFalse(form.is_bound)

    def test_post_new_club_redirects_when_not_logged_in(self):
        club_count_before = Club.objects.count()
        redirect_url = reverse('log_in')
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        club_count_after = Club.objects.count()
        self.assertEqual(club_count_after, club_count_before)

    def test_successful_new_club(self):
        self.client.login(email=self.user.email, password="Password123")
        club_count_before = Club.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        club_count_after = Club.objects.count()
        self.assertEqual(club_count_after, club_count_before+1)
        new_club = Club.objects.get(id=Club.objects.count())
        self.assertEqual(self.user, new_club.owner)
        response_url = reverse('club_list')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'club_list.html')

    def test_unsuccessful_new_club_creation_with_blank_name(self):
        self.client.login(email="johndoe@example.org",
                          password='Password123')
        club_count_before = Club.objects.count()
        self.data['name'] = ""
        response = self.client.post(self.url, self.data, follow=True)
        club_count_after = Club.objects.count()
        self.assertEqual(club_count_after, club_count_before)
        self.assertTemplateUsed(response, 'new_club.html')

    def test_unsuccessful_new_club_creation_with_blank_location(self):
        self.client.login(email="johndoe@example.org",
                          password='Password123')
        club_count_before = Club.objects.count()
        self.data['location'] = ""
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
        self.assertEqual(club_count_after, club_count_before+1)
        self.assertEqual(self.user, new_club.owner)
