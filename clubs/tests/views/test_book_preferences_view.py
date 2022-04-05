"""Tests of the book_preferences view."""

from clubs.models import Book, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse


class BookPreferencesViewTest(TestCase):
    """Tests of the book_preferences view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_book.json',
        'clubs/tests/fixtures/other_books.json',
        'clubs/tests/fixtures/default_rules.json',
        'clubs/tests/fixtures/seven_pos_ratings.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.first_book = Book.objects.get(pk=20)
        self.second_book = Book.objects.get(pk=27)
        self.data = {'q': self.first_book.title}
        self.url = reverse('book_preferences')

    def test_book_preferences_url(self):
        self.assertEqual(self.url, f'/book_preferences/')

    def test_get_book_preferences_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_alphabetic_book_list(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_preferences.html')
        self.assertEqual(len(response.context['books_paginated']), 12)

    def test_get_book_list_with_query(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url, self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_preferences.html')
        self.assertEqual(len(response.context['books_paginated']), 1)
        self.assertTrue(self.first_book in response.context['books_paginated'])
        self.assertFalse(self.second_book in response.context['books_paginated'])
