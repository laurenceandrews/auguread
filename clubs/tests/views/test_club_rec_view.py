"""Tests of the recommended clubs view."""

from clubs.models import Book, Club, Club_Books, ClubBookRecommendation, User
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
        self.data = {'q': self.club.name}
        self.url = reverse(
            'club_book_recommendations', kwargs={'club_id': self.club.id}
        )

    def test_clubs_recs_url(self):
        self.assertEqual(self.url,  f'/club/book/recommendations/{self.club.id}/')

    def test_get_clubs_recs_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_clubs_recs_list_with_recommendations(self):
        ClubBookRecommendation.objects.create(club=self.club, book=self.book)
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recommended_books_for_club_list.html')
        self.assertEqual(len(response.context['books']), 1)
