"""Tests for the book-to-club, age based recommender system"""

from django.test import TestCase
from numpy import empty
from clubs.models import User, Club, Club_Books, Book, Book_Rating, Club_Books, Club_Users
from clubs.book_to_user_recommender.book_to_user_knn import BookToUserRecommender

class AgeRecommenderSystemTestCase(TestCase):

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/default_book.json',
        'clubs/tests/fixtures/other_books.json',
        'clubs/tests/fixtures/default_rating.json',
        'clubs/tests/fixtures/other_ratings.json',
        'clubs/tests/fixtures/default_club_book.json',
        'clubs/tests/fixtures/default_club_user.json'
    ]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.recommender = BookToUserRecommender(user_id_to_query=self.user.id)

    def test_create_similarity_matrix(self):
        similarity_matrix = self.recommender.create_similarity_matrix()
        self.assertFalse(similarity_matrix is empty)

    def test_create_inner_id(self):
        inner_id = self.recommender.create_inner_id()
        self.assertFalse(inner_id is empty)

    def test_get_top_k_items_rated(self):
        top_k_items_rated = self.recommender.get_top_k_items_rated()
        self.assertFalse(top_k_items_rated is empty)

    def test_build_dictionary(self):
        dictionary = self.recommender.build_dictionary()
        self.assertFalse(dictionary is empty)

    def test_recommended_books(self):
        fav_book = self.recommender.build_dictionary()
        fav_book_id = fav_book[0]
        self.assertEquals(fav_book_id, self.recommender.get_recommended_books()[0])