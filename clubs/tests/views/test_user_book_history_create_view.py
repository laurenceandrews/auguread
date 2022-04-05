"""Tests of the user book history create view."""

from clubs.models import Book, User, User_Book_History
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse


class CreateUserBookHistoryViewTest(TestCase):
    """Tests of the user book history create view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_book.json',
        'clubs/tests/fixtures/other_books.json',
        'clubs/tests/fixtures/seven_pos_ratings.json'
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
            'create_user_book_history', kwargs={'user_id': self.user.id, 'book_id': self.book.id}
        )

    def test_create_user_book_history_url(self):
        self.assertEqual(self.url, f'/user/{self.user.id}/book/{self.book.id}/history/')

    def test_create_user_book_history_redirects_when_not_logged_in(self):
        user_book_history_count_before = User_Book_History.objects.count()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        user_book_history_count_after = User_Book_History.objects.count()
        self.assertEqual(user_book_history_count_after, user_book_history_count_before)

    def test_get_create_user_book_history(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_book_history_create.html')

    def test_successful_new_user_book_history(self):
        self.client.login(email=self.user.email, password="Password123")
        user_book_history_count_before = User_Book_History.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        user_book_history_count_after = User_Book_History.objects.count()
        self.assertEqual(user_book_history_count_after, user_book_history_count_before + 1)

    def test_successful_new_user_book_history_if_user_book_history_exists(self):
        User_Book_History.objects.create(book=self.book, user=self.user)
        self.client.login(email=self.user.email, password="Password123")
        user_book_history_count_before = User_Book_History.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        user_book_history_count_after = User_Book_History.objects.count()
        self.assertEqual(user_book_history_count_after, user_book_history_count_before)

    def test_unsuccessful_new_user_book_history(self):
        self.client.login(email=self.user.email, password="Password123")
        user_book_history_count_before = User_Book_History.objects.count()
        data = {
            "user": self.user,
            "book": 5
        }
        url = reverse(
            'create_user_book_history', kwargs={'user_id': self.user.id, 'book_id': 5}
        )
        response = self.client.post(url, data, follow=True)
        user_book_history_count_after = User_Book_History.objects.count()
        self.assertEqual(user_book_history_count_after, user_book_history_count_before)
