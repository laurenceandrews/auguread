"""Tests of the recommended clubs view."""

from clubs.models import Book, Club, Club_Books, User, UserClubRecommendation
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse


class ClubRecommenderViewTest(TestCase):
    """Tests of the recommended clubs view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/default_book.json',
        'clubs/tests/fixtures/default_rating.json',
        'clubs/tests/fixtures/default_club_book.json',
        'clubs/tests/fixtures/other_books.json',
        'clubs/tests/fixtures/seven_pos_ratings.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.club = Club.objects.get(pk=6)
        self.book = Book.objects.get(pk=20)
        self.second_club = Club.objects.get(pk=12)
        self.data = {'q': self.club.meeting_type}
        self.url = reverse(
            'club_recommender'
        )

    def test_clubs_recs_url(self):
        self.assertEqual(self.url,  f'/club_recommender/')

    def test_get_clubs_recs_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    # def test_get_clubs_recs_list_without_recommendations(self):
    #     self.client.login(email=self.user.email, password="Password123")
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'club_recommender.html')
    #     self.assertEqual(len(response.context['clubs_paginated']), 1)
    #     self.assertTrue(self.club in response.context['clubs_paginated'])

    def test_get_clubs_recs_list_with_recommendations(self):
        UserClubRecommendation.objects.create(club=self.club, user=self.user)
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_recommender.html')
        self.assertEqual(len(response.context['clubs_paginated']), 1)
        self.assertTrue(self.club in response.context['clubs_paginated'])

    def est_get_clubs_recs_list_with_recommendations_with_query(self):
        UserClubRecommendation.objects.create(club=self.club, user=self.user)
        self.second_club = Club.objects.get(pk=12)
        UserClubRecommendation.objects.create(club=self.second_club, user=self.user)
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url, self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_recommender.html')
        self.assertEqual(len(response.context['clubs_paginated']), 1)
        self.assertTrue(self.club in response.context['clubs_paginated'])
        self.assertFalse(self.second_club in response.context['clubs_paginated'])
