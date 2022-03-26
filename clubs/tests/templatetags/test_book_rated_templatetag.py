from clubs.models import Book, Book_Rating, User
from clubs.templatetags.book_rated import book_rated
from django.test import TestCase


class BookRatedTemplatetagTestCase(TestCase):

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_book.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.book = Book.objects.get(pk=20)
        self.book_rating = Book_Rating.objects.create(book=self.book, user=self.user, rating=5)

    def test_valid_input_with_existing_book_rating(self):
        result = book_rated(self.book, self.user)
        self.assertEqual(result, f'Current rating: {self.book_rating.rating}')

    def test_valid_input_with_no_existing_book_rating(self):
        user = User.objects.get(pk=2)
        result = book_rated(self.book, user)
        self.assertEqual(result, "Current rating: None")
