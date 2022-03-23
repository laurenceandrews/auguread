"""Tests of the book rating create view."""
import datetime

import pytz
from clubs.models import Book, Book_Rating, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from schedule.models import Calendar, Event, Rule


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

    # def test_succesful_create_book_rating(self):
    #     self.client.login(email=self.user.email, password="Password123")
    #     book_rating_count_before = Book_Rating.objects.count()
    #     response = self.client.post(self.url, self.data, follow=True)
    #     book_rating_count_after = Book_Rating.objects.count()
    #     self.assertEqual(book_rating_count_after, book_rating_count_before + 1)

    def test_succesful_create_book_rating(self):
        self.client.login(email=self.user.email, password="Password123")
        book_rating_count_before = Book_Rating.objects.count()
        response = self.client.get(self.url, self.data, follow=True)

        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.url, self.data, follow=True)
        self.assertEqual(response.status_code, 404)
        book_rating_count_after = Book_Rating.objects.count()
        self.assertEqual(book_rating_count_after, book_rating_count_before + 1)

    def test_unsuccesful_create_book_rating(self):
        self.data = {}
        self.client.login(email=self.user.email, password="Password123")
        book_rating_count_before = Book_Rating.objects.count()
        response = self.client.get(self.url, self.data, follow=True)

        self.assertEqual(response.status_code, 200)

        esponse = self.client.post(self.url, self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        book_rating_count_after = Book_Rating.objects.count()
        self.assertEqual(book_rating_count_after, book_rating_count_before)
        self.assertTemplateUsed(response, 'book_rating_create.html')
