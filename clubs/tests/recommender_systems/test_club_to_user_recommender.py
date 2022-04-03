# """Tests for the book-to-club, author based recommender system"""

# from venv import create
# from django.test import TestCase
# from numpy import empty
# from clubs.models import Club, Book, User, Club_Books, Club_Users, Book_Rating
# from clubs.club_to_user_recommender.club_to_user_recommender import ClubUserRecommender

# class AuthorRecommenderSystemTestCase(TestCase):

#     fixtures = [
#         'clubs/tests/fixtures/default_user.json',
#         'clubs/tests/fixtures/other_users.json',
#         'clubs/tests/fixtures/default_calendar.json',
#         'clubs/tests/fixtures/default_club.json',
#         'clubs/tests/fixtures/default_book.json',
#         'clubs/tests/fixtures/other_books.json',
#         'clubs/tests/fixtures/default_rating.json',
#         'clubs/tests/fixtures/other_ratings.json',
#         'clubs/tests/fixtures/default_club_book.json',
#         'clubs/tests/fixtures/default_club_user.json'
#     ]

#     def setUp(self):
#         self.user = User.objects.get(pk=1)
#         self.club = Club.objects.get(pk=6)
#         self.club_user = Club_Users.objects.get(pk=1)
#         self.recommender = ClubUserRecommender(user_id=self.user.id)

#     def test_get_user(self):
#         user = self.recommender.get_user()
#         self.assertEqual(self.user, user)

#     def test_get_user_age_df_is_not_empty(self):
#         user_age_df = self.recommender.get_user_age_df()
#         self.assertFalse(user_age_df is empty)

#     def test_get_club_locations_df_is_not_empty(self):
#         club_locations_df = self.recommender.get_club_locations_df()
#         self.assertFalse(club_locations_df is empty)
    
#     def test_get_average_club_age_df_is_not_empty(self):
#         average_club_age_df = self.recommender.get_average_club_age_df()
#         self.assertFalse(average_club_age_df is empty)

#     def test_get_age_difference_df_is_not_empty(self):
#         age_difference_df = self.recommender.get_age_difference_df()
#         self.assertFalse(age_difference_df is empty)

#     def test_get_top_10_by_closest_age_df_is_not_empty(self):
#         top_10_by_closest_age = self.recommender.get_top_10_by_closest_age()
#         self.assertFalse(top_10_by_closest_age is empty)

#     def test_get_user_count_per_club_df_is_not_empty(self):
#         club_user_count_per_club_df = self.recommender.get_club_user_count_per_club()
#         self.assertFalse(club_user_count_per_club_df is empty)

#     def test_get_ratio_loc(self):
#         pass

#     def test_get_clubs_with_matching_loc_fuzzy_df_is_not_empty(self):
#         clubs_with_matching_loc_fuzzy_df = self.recommender.get_clubs_with_matching_loc_fuzzy()
#         self.assertFalse(clubs_with_matching_loc_fuzzy_df is empty)

#     def test_get_club_favourite_books_df_is_not_empty(self):
#         club_favourite_books_df = self.recommender.get_club_favourite_books()
#         self.assertFalse(club_favourite_books_df is empty)

#     def test_get_user_favourite_books_df_is_not_empty(self):
#         user_favourite_books_df = self.recommender.get_user_favourite_books()
#         self.assertFalse(user_favourite_books_df is empty)

#     def test_get_fav_books_and_authors_per_user_is_not_empty(self):
#         fav_books_and_authors_per_user_df = self.recommender.get_fav_books_and_authors_per_user()
#         self.assertFalse(fav_books_and_authors_per_user_df is empty)

#     def test_get_all_favourite_book_matches_fuzzy_df_is_not_empty(self):
#         all_favourite_book_matches_fuzzy_df = self.recommender.get_all_favourite_book_matches_fuzzy()
#         self.assertFalse(all_favourite_book_matches_fuzzy_df is empty)

#     def test_get_average_book_match_df_is_not_empty(self):
#         average_book_match_df = self.recommender.get_average_book_match_df()
#         self.assertFalse(average_book_match_df is empty)

#     def test_get_all_favourite_author_matches_fuzzy_df_is_not_empty(self):
#         all_favourite_author_matches_fuzzy_df = self.recommender.get_all_favourite_author_matches_fuzzy()
#         self.assertFalse(all_favourite_author_matches_fuzzy_df is empty)

#     def test_get_club_average_author_match_df_is_not_empty(self):
#         club_average_author_match_df = self.recommender.get_club_average_author_match_df()
#         self.assertFalse(club_average_author_match_df is empty)

#     def test_get_best_clubs_df_is_not_empty(self):
#         best_clubs_df = self.recommender.get_best_clubs_df()
#         self.assertFalse(best_clubs_df is empty)

#     def test_get_best_clubs_in_person_is_not_empty(self):
#         best_clubs_in_person_df = self.recommender.get_best_clubs_in_person()
#         self.assertFalse(best_clubs_in_person_df is empty)

#     def test_get_best_clubs_online_is_not_empty(self):
#         best_clubs_online_df = self.recommender.get_best_clubs_online()
#         self.assertFalse(best_clubs_online_df is empty)

#     def test_get_best_clubs_in_person(self):
#         recommended_clubs = self.recommender.get_best_clubs_in_person()
#         print(recommended_clubs[0])    
#         print(recommended_clubs[1])    
#         # self.assertEqual(recommended_clubs[0], 19)    
#         # self.assertEqual(recommended_clubs[1], 39)

#     def test_get_best_clubs_online(self):
#         recommended_clubs = self.recommender.get_best_clubs_online()
#         print(recommended_clubs[0])    
#         print(recommended_clubs[1])    
#         # self.assertEqual(recommended_clubs[0], 19)    
#         # self.assertEqual(recommended_clubs[1], 39)

#     # EXAMPLES

#     def test_get_club_fav_books(self):
#         club_fav_book = self.recommender.getClubFavBooks()
#         self.assertTrue(Club_Books.objects.filter(club=self.club, book=club_fav_book['book_id'].iloc[0]).exists())

#     def test_get_fav_book_authors(self):
#         fav_book, fav_author = self.recommender.getFavBooksAuthors()
#         fav_book_id = fav_book['book_id'].iloc[0]
#         self.assertTrue(Book.objects.filter(id=fav_book_id, author=fav_author[0]).exists())

#     def test_get_author_books(self):
#         author_book = self.recommender.getAuthorBooks()
#         self.assertTrue(Book.objects.filter(ISBN=author_book['ISBN'].iloc[0], author=author_book['author'].iloc[0]).exists())

#     def test_get_recommended_books(self):
#         recommended_books = self.recommender.get_recommended_books()
#         self.assertEqual(recommended_books[0], 19)    
#         self.assertEqual(recommended_books[1], 39)    
