"""Tests for the update profile view."""
from clubs.forms import ClubUpdateForm
from clubs.models import Club, User
from clubs.tests.helpers import reverse_with_next
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse


class ClubUpdateViewTestCase(TestCase):

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_rules.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_clubs.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.club = Club.objects.get(pk=6)
        self.form_input = {
            "name": "Pink Club",
            "description": "A club that reads lots of pink books.",
            "meeting_type": "ONL"
        }

        self.url = reverse(
            'club_update', kwargs={'club_id': self.club.id}
        )

    def test_club_update_url(self):
        self.assertEqual(self.url, f'/club/update/{self.club.id}')

    def test_get_club_update(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_update_view.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ClubUpdateForm))
        self.assertEqual(form.instance, self.club)

    def test_get_club_update_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_update_club_redirects_when_not_a_club_owner(self):
        club_not_owner = Club.objects.get(pk=16)
        form_input = {}
        url = reverse(
            'club_update', kwargs={'club_id': club_not_owner.id}
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

    def test_unsuccesful_club_update(self):
        self.client.login(email=self.user.email, password="Password123")
        self.form_input["name"] = ""
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "club_update_view.html")
        form = response.context["form"]
        self.assertTrue(isinstance(form, ClubUpdateForm))
        self.assertTrue(form.is_bound)
        self.club.refresh_from_db()
        self.assertEqual(self.club.name, "Fun Club")
        self.assertEqual(self.club.description, "A club that reads lots of fun books.")
        self.assertEqual(self.club.meeting_type, "ONL")

    def test_succesful_club_update(self):
        self.client.login(email=self.user.email, password='Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('club_detail', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club_detail.html')
        self.club.refresh_from_db()
        self.assertEqual(self.club.name, self.form_input['name'])
        self.assertEqual(self.club.description, self.form_input['description'])
        self.assertEqual(self.club.meeting_type, self.form_input['meeting_type'])

    def test_post_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(
            response, redirect_url, status_code=302, target_status_code=200
        )
