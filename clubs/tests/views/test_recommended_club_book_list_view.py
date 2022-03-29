"""Tests of the list of recommended books for a club view."""

from clubs.models import Book, Club, Club_Books, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse


class RecommendedClubBookListViewTest(TestCase):
    """Tests of the list of recommended books for a club view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/default_book.json',
        'clubs/tests/fixtures/default_rating.json',
        'clubs/tests/fixtures/default_club_book.json',
        'clubs/tests/fixtures/default_club_user.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.club = Club.objects.get(pk=6)
        self.second_club = Club.objects.get(pk=12)
        self.data = {'q': self.club.name}
        self.url = reverse(
            'club_book_recommendations', kwargs={'club_id': self.club.id}
        )

    def test_club_list_url(self):
        self.assertEqual(self.url,  f'/club/book/recommendations/{self.club.id}/')

    def test_get_club_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_club_list(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recommended_books_for_club_list.html')
        self.assertEqual(len(response.context['books']), 1)

    # def test_get_club_list_with_author_books_is_empty(self):
    #     pass
