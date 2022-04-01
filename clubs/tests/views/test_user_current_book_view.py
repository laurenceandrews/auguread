"""Tests of the user current book view."""
from clubs.models import Book, User, User_Book_History
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse


class UserCurrentBookViewTestCase(TestCase):
    """Tests of the user current book view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_book.json',
        'clubs/tests/fixtures/other_books.json'
    ]

    def setUp(self):
        self.url = reverse('user_current_book')
        self.user = User.objects.get(email='johndoe@example.org')
        self.first_book = Book.objects.get(pk=20)
        self.second_book = Book.objects.get(pk=24)

    def test_user_current_book_url(self):
        self.assertEqual(self.url, '/summary/books/current')

    def test_get_user_book_current(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_current_book.html')

    def test_get_user_current_book_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_user_current_book_shows_current_book_when_user_has_one_user_book_history(self):
        self.client.login(email=self.user.email, password="Password123")
        User_Book_History.objects.create(user=self.user, book=self.first_book)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_current_book.html')
        self.assertContains(response, f'{self.first_book.title}', status_code=200)

    def test_user_current_book_shows_current_book_when_user_has_multiple_user_book_history(self):
        self.client.login(email=self.user.email, password="Password123")
        User_Book_History.objects.create(user=self.user, book=self.first_book)
        User_Book_History.objects.create(user=self.user, book=self.second_book)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_current_book.html')
        self.assertNotContains(response, f'{self.first_book.title}', status_code=200)
        self.assertContains(response, f'{self.second_book.title}', status_code=200)

    def test_user_current_book_shows_message_when_user_has_no_user_book_history(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_current_book.html')
        self.assertContains(response, "<p>You haven't set any books as currently reading yet.</p>", status_code=200)
        self.assertNotContains(response, f'{self.first_book.title}', status_code=200)
        self.assertNotContains(response, f'{self.second_book.title}', status_code=200)
