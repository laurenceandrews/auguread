from clubs.models import Book, User, Book_Rating
from clubs.views.mixins import TenPosRatingsRequiredMixin
from django.test import TestCase
from django.urls import reverse
from clubs.tests.helpers import reverse_with_next
from django.shortcuts import redirect
from django.conf import settings
from django.http import HttpRequest
from django.test.client import Client


class TenPosRatingsRequiredMixinTestCase(TestCase):

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_book.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self.book = Book.objects.get(pk=20)

        self.request = HttpRequest()
        self.request.user = self.user

        self.client = Client()
        self.client.login(email="johndoe@example.org", password="Password123")

        self.mixin = TenPosRatingsRequiredMixin()
        self.redirect_when_less_than_ten_pos_ratings_url = reverse(settings.REDIRECT_URL_WHEN_NOT_ENOUGH_RATINGS)

    def test_redirect(self):        
        response = self.client.get(reverse('club_recommender'))
        redirect_url = self.redirect_when_less_than_ten_pos_ratings_url

        self.assertRedirects(
            response,
            redirect_url,
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True)

    def test_handle_less_than_ten_pos_ratings(self):
        pass

    def test_valid_input_for_at_least_ten_pos_ratings(self):
        book_ratings = []
        for i in range(10):
            book_rating = Book_Rating.objects.create(book=self.book, user=self.user, rating=6)
            book_ratings.append(book_rating)
        result = self.mixin.has_less_than_ten_pos_ratings(self.user)
        self.assertEqual(result, False)
        
    def test_invalid_input_for_less_than_ten_pos_ratings(self):
        book_ratings = []
        for i in range(9):
            book_rating = Book_Rating.objects.create(book=self.book, user=self.user, rating=6)
            book_ratings.append(book_rating)
        result = self.mixin.has_less_than_ten_pos_ratings(self.user)
        self.assertEqual(result, True)
