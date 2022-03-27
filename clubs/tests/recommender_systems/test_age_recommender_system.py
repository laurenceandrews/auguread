"""Tests for the book-to-club, age based recommender system"""

from django.test import TestCase
from numpy import empty
from clubs.models import User, Club, Club_Books
from clubs.book_to_club_recommender.book_to_club_recommender_age import ClubBookAgeRecommender

class AgeRecommenderSystemTestCase(TestCase):

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/default_book.json',
        'clubs/tests/fixtures/default_club_book.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/other_clubs.json',
        'clubs/tests/fixtures/default_club_user.json',
        'clubs/tests/fixtures/other_club_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.club = Club.objects.get(pk=6)
        self.recommender = ClubBookAgeRecommender(club_id_to_query=self.club.id)

    def test_clubs_average_ages(self):
        clubs_average_ages = self.recommender.club_average_ages()
        self.assertFalse(clubs_average_ages is empty)

    def test_clubs_closest_in_age(self):
        closest_clubs_in_age = self.recommender.find_closest_clubs_in_age()
        self.assertFalse(closest_clubs_in_age is empty)

    def test_recommended(self):
        recommended_books = self.recommender.get_recommended_books()
        self.assertFalse(recommended_books is empty)    

    def test_average_age(self):
        average_ages = self.recommender.club_average_ages()
        average_age = average_ages['average_age'].iloc[0]
        self.assertEqual(average_age, self.user.age)

    def test_age_difference(self):
        closest_clubs_in_age = self.recommender.find_closest_clubs_in_age()
        self.assertEqual(closest_clubs_in_age['id'].iloc[0], Club.objects.get(pk=12).id)
        self.assertEqual(closest_clubs_in_age['id'].iloc[1], Club.objects.get(pk=23).id)

    def test_recommended_books(self):
        recommended_books = self.recommender.get_recommended_books()
        for book in recommended_books:
            self.assertTrue(Club_Books.objects.exists(book=book))
