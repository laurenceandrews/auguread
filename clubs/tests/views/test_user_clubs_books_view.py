"""Tests of the user clubs' books view."""
from clubs.models import (Book, Club, Club_Book_History, Club_Books,
                          Club_Users, User)
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse


class UserFavouriteBooksViewTestCase(TestCase):
    """Tests of the user clubs' books view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_book.json',
        'clubs/tests/fixtures/other_books.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_clubs.json',
        'clubs/tests/fixtures/default_rules.json',
        'clubs/tests/fixtures/seven_pos_ratings.json'
    ]

    def setUp(self):
        self.url = reverse('user_clubs_books')
        self.user = User.objects.get(email='johndoe@example.org')
        self.first_book = Book.objects.get(pk=20)
        self.second_book = Book.objects.get(pk=24)
        self.third_book = Book.objects.get(pk=27)
        self._create_club_books()

    def test_user_clubs_books_url(self):
        self.assertEqual(self.url, '/summary/books/clubs')

    def test_get_clubs_favourite_books(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/books_table.html')

    def test_get_user_clubs_books_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_user_clubs_books_shows_clubs_book_when_user_is_a_member_or_owner_of_a_club_with_existing_book_histories(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/books_table.html')
        self.assertEqual(len(response.context['books']), 2)
        self.assertContains(response, f'{self.first_book.title}', status_code=200)
        self.assertContains(response, f'{self.second_book.title}', status_code=200)

    def test_user_clubs_books_does_not_show_clubs_book_when_user_is_an_applicant_of_a_club_with_existing_book_histories(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/books_table.html')
        self.assertContains(response, f'{self.first_book.title}', status_code=200)
        self.assertContains(response, f'{self.second_book.title}', status_code=200)
        self.assertNotContains(response, f'{self.third_book.title}', status_code=200)

    def test_user_clubs_books_shows_message_user_is_not_a_member_or_owner_of_a_club_with_existing_favourite_books(self):
        user = User.objects.get(username="@peterpickles")
        club_with_no_favourites = Club.objects.get(pk=12)
        Club_Users.objects.create(user=user, club=club_with_no_favourites, role_num="1")
        self.client.login(email=user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'partials/books_table.html')
        self.assertContains(response, '<p>No books to show.</p>', status_code=200)
        self.assertNotContains(response, f'{self.first_book.title}', status_code=200)
        self.assertNotContains(response, f'{self.second_book.title}', status_code=200)
        self.assertNotContains(response, f'{self.third_book.title}', status_code=200)

    def test_user_clubs_books_with_query(self):
        self.client.login(email=self.user.email, password="Password123")
        data_with_q = {'q': self.first_book.title}
        response = self.client.get(self.url, data_with_q, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/books_table.html')
        self.assertEqual(len(response.context['books']), 1)
        self.assertContains(response, f'{self.first_book.title}', status_code=200)
        self.assertNotContains(response, f'{self.second_book.title}', status_code=200)
        self.assertNotContains(response, f'{self.third_book.title}', status_code=200)

    def _create_club_books(self):
        self.club_as_owner = Club.objects.get(pk=6)
        Club_Book_History.objects.create(club=self.club_as_owner, book=self.first_book, average_rating=5)

        self.club_as_member = Club.objects.get(pk=16)
        Club_Users.objects.create(user=self.user, club=self.club_as_member, role_num="2")
        Club_Book_History.objects.create(club=self.club_as_member, book=self.second_book, average_rating=5)

        self.club_as_applicant = Club.objects.get(pk=26)
        Club_Users.objects.create(user=self.user, club=self.club_as_applicant, role_num="1")
        Club_Book_History.objects.create(club=self.club_as_applicant, book=self.third_book, average_rating=5)
