"""Tests of the user favourite books view."""
from clubs.models import Book, User, User_Books
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse


class UserFavouriteBooksViewTestCase(TestCase):
    """Tests of the user favourite books view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_book.json',
        'clubs/tests/fixtures/other_books.json'
    ]

    def setUp(self):
        self.url = reverse('user_favourite_books')
        self.user = User.objects.get(email='johndoe@example.org')
        self.first_book = Book.objects.get(pk=20)
        self.second_book = Book.objects.get(pk=24)

    def test_user_favourite_books_url(self):
        self.assertEqual(self.url, '/summary/books/favourite')

    def test_get_user_favourite_books(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/books_table.html')

    def test_get_user_favourite_books_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_user_favourite_books_shows_favourite_book_when_user_has_existing_favourite_books(self):
        self.client.login(email=self.user.email, password="Password123")
        User_Books.objects.create(user=self.user, book=self.first_book)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/books_table.html')
        self.assertContains(response, f'{self.first_book.title}', status_code=200)
        self.assertNotContains(response, f'{self.second_book.title}', status_code=200)

    def test_user_favourite_books_shows_message_when_user_has_no_favourite_books(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/books_table.html')
        self.assertContains(response, '<p>No books to show.</p>', status_code=200)
        self.assertNotContains(response, f'{self.first_book.title}', status_code=200)
        self.assertNotContains(response, f'{self.second_book.title}', status_code=200)
