# """Tests for the book-to-club, author based recommender system"""

# from venv import create
# from django.test import TestCase
# from numpy import empty
# from clubs.models import Club, Book, Club_Books, Club_Users, Book_Rating
# from clubs.forms import PostForm
# from clubs.book_to_club_recommender.book_to_club_recommender_author import ClubBookAuthorRecommender

# class AuthorRecommenderSystemTestCase(TestCase):

#     fixtures = [
#         'clubs/tests/fixtures/default_user.json',
#         'clubs/tests/fixtures/default_calendar.json',
#         'clubs/tests/fixtures/default_club.json',
#         'clubs/tests/fixtures/default_book.json',
#         'clubs/tests/fixtures/default_rating.json',
#         'clubs/tests/fixtures/default_club_book.json',
#         'clubs/tests/fixtures/default_club_user.json'
#     ]

#     def setUp(self):
#         self.club = Club.objects.get(pk=6)
#         self.book = Book.objects.get(pk=20)
#         self.club_user = Club_Users.objects.get(pk=1)
#         self.recommender = ClubBookAuthorRecommender(club_id_to_query=self.club.id)

#     def test_clubs_average_ages(self):
#         clubs_average_ages = self.recommender.club_average_ages
#         self.assertFalse(clubs_average_ages is empty)

#     def test_clubs_closest_in_age(self):
#         closest_clubs_in_age = self.recommender.find_closest_clubs_in_age
#         self.assertFalse(closest_clubs_in_age is empty)

#     def test_recommended(self):
#         recommended_books = self.recommender.get_recommended_books
#         self.assertFalse(len(recommended_books) is empty)       


#     def make_user_ratings(self):

#         for i in range(10):
#             Book_Rating.objects.create(
#             )