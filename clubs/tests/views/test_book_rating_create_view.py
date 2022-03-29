"""Tests of the book rating create view."""

from clubs.models import Book, Book_Rating, User
from clubs.tests.helpers import reverse_with_next
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse


class CreateBookRatingViewTest(TestCase):
    """Tests of the create_event view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_book.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self.book = Book.objects.get(pk=20)

        self.data = {
            'rating': 5
        }

        self.url = reverse(
            'rate_book', kwargs={'book_id': self.book.id}
        )

    def test_create_online_book_rating_url(self):
        self.assertEqual(self.url, f'/book/rating/{self.book.id}/')

    def test_create_book_rating_redirects_when_not_logged_in(self):
        data = {}
        book_rating_count_before = Book_Rating.objects.count()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, data, follow=True)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        book_rating_count_after = Book_Rating.objects.count()
        self.assertEqual(book_rating_count_after, book_rating_count_before)

    def test_get_create_book_rating(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'book_rating_create.html')

    def test_get_create_book_rating_with_invalid_book_id(self):
        url = reverse(
            'rate_book', kwargs={'book_id': 0}
        )
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_rating_create.html')
        # messages_list = list(response.context['messages'])
        # self.assertEqual(len(messages_list), 1)
        # self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_succesful_create_book_rating(self):
        self.client.login(email=self.user.email, password="Password123")
        book_rating_count_before = Book_Rating.objects.count()
        response = self.client.get(self.url, self.data, follow=True)

        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.url, self.data, follow=True)
        self.assertEqual(response.status_code, 404)
        book_rating_count_after = Book_Rating.objects.count()
        self.assertEqual(book_rating_count_after, book_rating_count_before + 1)

    def test_succesful_create_book_rating_when_book_rating_exists(self):
        book_rating = Book_Rating.objects.create(book=self.book, user=self.user, rating=1)
        self.client.login(email=self.user.email, password="Password123")
        book_rating_count_before = Book_Rating.objects.count()
        response = self.client.get(self.url, self.data, follow=True)

        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.url, self.data, follow=True)
        self.assertEqual(response.status_code, 404)
        book_rating_count_after = Book_Rating.objects.count()
        self.assertEqual(book_rating_count_after, book_rating_count_before)
        book_rating = Book_Rating.objects.get(book=self.book, user=self.user)
        self.assertEqual(book_rating.rating, str(self.data['rating']))

    def test_unsuccesful_create_book_rating(self):
        self.data = {}
        self.client.login(email=self.user.email, password="Password123")
        book_rating_count_before = Book_Rating.objects.count()
        response = self.client.get(self.url, self.data, follow=True)

        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.url, self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        book_rating_count_after = Book_Rating.objects.count()
        self.assertEqual(book_rating_count_after, book_rating_count_before)
        self.assertTemplateUsed(response, 'book_rating_create.html')
