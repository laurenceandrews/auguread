"""Tests of the user book delete view."""

from clubs.models import Book, User, User_Books
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse


class deleteUserBookHistoryViewTest(TestCase):
    """Tests of the user book delete view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_book.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self.book = Book.objects.get(pk=20)
        User_Books.objects.create(user=self.user, book=self.book)

        self.data = {
            "user": self.user,
            "book": self.book
        }
        self.url = reverse(
            'delete_user_book_favourite', kwargs={'user_id': self.user.id, 'book_id': self.book.id}
        )

    def test_delete_user_books_url(self):
        self.assertEqual(self.url, f'/user/{self.user.id}/book/{self.book.id}/favourite/delete/')

    def test_delete_user_books_redirects_when_not_logged_in(self):
        user_books_count_before = User_Books.objects.count()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        user_books_count_after = User_Books.objects.count()
        self.assertEqual(user_books_count_after, user_books_count_before)

    # def test_get_delete_user_books(self):
    #     self.client.login(email=self.user.email, password="Password123")
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, 200)

    def test_successful_delete_user_books(self):
        self.client.login(email=self.user.email, password="Password123")
        user_books_count_before = User_Books.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        user_books_count_after = User_Books.objects.count()
        self.assertEqual(user_books_count_after + 1, user_books_count_before)

    def test_unsuccessful_delete_user_books(self):
        self.client.login(email=self.user.email, password="Password123")
        user_books_count_before = User_Books.objects.count()
        data = {
            "user": self.user,
            "book": 5
        }
        url = reverse(
            'delete_user_book_favourite', kwargs={'user_id': self.user.id, 'book_id': 5}
        )
        response = self.client.post(url, data, follow=True)
        user_books_count_after = User_Books.objects.count()
        self.assertEqual(user_books_count_after, user_books_count_before)
