"""Unit tests for the club book select page."""

from clubs.models import Book, Club, Club_Book_History, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse
from schedule.models import Calendar


class ClubBookSelectViewTest(TestCase):

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
        self.calendar = Calendar.objects.get(pk=5)
        self.club = Club.objects.get(pk=6)
        self.book = Book.objects.get(pk=20)

        self.url = reverse('club_book_select', kwargs={'club_id': self.club.id, 'book_id': self.book.id})

    def test_club_book_select_url(self):
        self.assertEqual(self.url, f'/club/{self.club.id}/book/{self.book.id}/select/')

    def test_get_club_book_select_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_club_book_select_with_valid_club_and_book_ids(self):
        self.client.login(email=self.user.email, password="Password123")
        club_book_history_count_before = Club_Book_History.objects.count()
        response = self.client.get(self.url)
        club_book_history_count_after = Club_Book_History.objects.count()
        self.assertEqual(club_book_history_count_after, club_book_history_count_before + 1)

    def test_unsuccesful_club_book_select(self):
        self.client.login(email=self.user.email, password="Password123")
        club_book_history_count_before = Club_Book_History.objects.count()
        url = reverse('club_book_select', kwargs={'club_id': 0, 'book_id': 0})
        response = self.client.post(url)
        club_book_history_count_after = Club_Book_History.objects.count()
        self.assertEqual(club_book_history_count_after, club_book_history_count_before)
