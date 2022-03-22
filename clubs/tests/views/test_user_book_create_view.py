"""Tests of the user book create view."""

from clubs.models import Book, User, User_Books
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse


class CreateUserBookHistoryViewTest(TestCase):
    """Tests of the user book create view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_book.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self.book = Book.objects.get(pk=20)

        self.data = {
            "user": self.user,
            "book": self.book
        }
        self.url = reverse(
            'create_user_book_favourite', kwargs={'user_id': self.user.id, 'book_id': self.book.id}
        )

    def test_create_user_books_url(self):
        self.assertEqual(self.url, f'/user/{self.user.id}/book/{self.book.id}/favourite/')

    def test_create_user_books_redirects_when_not_logged_in(self):
        user_books_count_before = User_Books.objects.count()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        user_books_count_after = User_Books.objects.count()
        self.assertEqual(user_books_count_after, user_books_count_before)

    def test_get_create_user_books(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_books_create.html')

    def test_successful_new_user_books(self):
        self.client.login(email=self.user.email, password="Password123")
        user_books_count_before = User_Books.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        user_books_count_after = User_Books.objects.count()
        self.assertEqual(user_books_count_after, user_books_count_before + 1)

    def test_unsuccessful_new_User_Books(self):
        self.client.login(email=self.user.email, password="Password123")
        user_books_count_before = User_Books.objects.count()
        data = {
            "user": self.user,
            "book": 5
        }
        url = reverse(
            'create_user_book_favourite', kwargs={'user_id': self.user.id, 'book_id': 5}
        )
        response = self.client.post(url, data, follow=True)
        user_books_count_after = User_Books.objects.count()
        self.assertEqual(user_books_count_after, user_books_count_before)
