"""Tests for the book-to-club, author based recommender system"""

from venv import create
from django.test import TestCase
from numpy import empty
from clubs.models import Club, Book, User, Club_Books, Club_Users, Book_Rating
from clubs.book_to_club_recommender.book_to_club_recommender_author import ClubBookAuthorRecommender

class AuthorRecommenderSystemTestCase(TestCase):

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
        self.club = Club.objects.get(pk=6)
        self.club_user = Club_Users.objects.get(pk=1)
        self.recommender = ClubBookAuthorRecommender(club_id_to_query=self.club.id)

    def test_get_club_fav_books_is_not_empty(self):
        club_fav_books = self.recommender.getClubFavBooks()
        self.assertFalse(club_fav_books is empty)

    def test_get_club_fav_authors_is_not_empty(self):
        club_fav_authors = self.recommender.getFavBooksAuthors()
        self.assertFalse(club_fav_authors is empty)

    def test_get_author_books_is_not_empty(self):
        author_books = self.recommender.getAuthorBooks()
        self.assertFalse(author_books is empty)

    def test_recommended_is_not_empty(self):
        recommended_books = self.recommender.get_recommended_books()
        self.assertFalse(recommended_books is empty)    

    def test_get_club_fav_books(self):
        club_fav_book = self.recommender.getClubFavBooks()
        self.assertTrue(Club_Books.objects.filter(club=self.club, book=club_fav_book['book_id'].iloc[0]).exists())

    def test_get_fav_book_authors(self):
        fav_book, fav_author = self.recommender.getFavBooksAuthors()
        fav_book_id = fav_book['book_id'].iloc[0]
        self.assertTrue(Book.objects.filter(id=fav_book_id, author=fav_author[0]).exists())

    def test_get_author_books(self):
        author_book = self.recommender.getAuthorBooks()
        self.assertTrue(Book.objects.filter(ISBN=author_book['ISBN'].iloc[0], author=author_book['author'].iloc[0]).exists())

    def test_get_recommended_books(self):
        recommended_books = self.recommender.get_recommended_books()
        self.assertEqual(recommended_books[0], 19)    
        self.assertEqual(recommended_books[1], 39)    
