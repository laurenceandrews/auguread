"""Unit tests for the UserBookHistory model."""
from clubs.models import Book, User, User_Book_History
from django.core.exceptions import ValidationError
from django.test import TestCase


class UserBookHistoryTest(TestCase):
    """Unit tests for the UserBookHistory model."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_book.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self.book = Book.objects.get(pk=20)
        self.user_book_history = User_Book_History(user=self.user, book=self.book)

    def test_valid_user_book_history(self):
        try:
            self.user_book_history.full_clean()
        except ValidationError:
            self.fail("Test user_book_history should be valid")

    def test_user_must_not_be_blank(self):
        self.user_book_history.user = None
        with self.assertRaises(ValidationError):
            self.user_book_history.full_clean()

    def test_book_must_not_be_blank(self):
        self.user_book_history.book = None
        with self.assertRaises(ValidationError):
            self.user_book_history.full_clean()
