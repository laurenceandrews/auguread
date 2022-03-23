from clubs.models import Book, User, Book_Rating
from clubs.views.mixins import TenPosRatingsRequiredMixin
from django.test import TestCase
from django.urls import reverse
from django.shortcuts import redirect
from django.conf import settings


class TenPosRatingsRequiredMixinTestCase(TestCase):

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_book.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.mixin = TenPosRatingsRequiredMixin()
        self.user = User.objects.get(pk=1)
        self.book = Book.objects.get(pk=20)
        self.redirect_when_less_than_ten_pos_ratings_url = settings.REDIRECT_URL_WHEN_NOT_ENOUGH_RATINGS

    def test_dispatch(self):
        pass

    def test_handle_less_than_ten_pos_ratings(self):
        pass
        # result = self.mixin.handle_less_than_ten_pos_ratings()
        # self.assertEqual(result, redirect(self.redirect_when_less_than_ten_pos_ratings_url))

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
