"""Unit test for the enter view"""
from clubs.models import Club, User
from django.urls import reverse
from django.conf import settings
from django.test import TestCase



class EnterViewTestCase(TestCase):
    fixtures = [
        'clubs/tests/fixtures/club.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.owner = Club.objects.get(id=1).owner
        self.url = reverse('enter', kwargs={'club_id': self.club.id})
        self.applicant = User.objects.get(id = 447)

    def test_enter_club(self):
        self.client.login(email=self.owner.email, password='Password123')
        response = self.client.get(self.url)
        redirect_url = reverse('show_user', kwargs={
                               'club_id': self.club.id, 'user_id': self.owner.id})
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)


    def test_applicant_should_not_be_able_to_enter_club(self):

        self.client.login(email=self.applicant.email, password='Password123')
        response = self.client.get(self.url)
        redirect_url = reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)
