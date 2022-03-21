"""Unit tests of the club book form."""
from clubs.forms import ClubBookForm
from clubs.models import Book, Club, Club_Book_History, User
from django.test import TestCase
from schedule.models import Calendar


class ClubBookFormTestCase(TestCase):
    """Unit tests of club book form."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/default_book.json',
        'clubs/tests/fixtures/default_rating.json',
        'clubs/tests/fixtures/default_club_book.json',
        'clubs/tests/fixtures/default_club_user.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.calendar = Calendar.objects.get(pk=5)
        self.book = Book.objects.get(pk=20)
        self.club = Club.objects.get(pk=6)
        self._create_club_book_history()
        self.form_input = {
            'book': self.book
        }

    def test_form_has_necessary_fields(self):
        form = ClubBookForm(club_id=self.club.id)
        self.assertIn('book', form.fields)

    def test_club_book_history_is_made(self):
        self.assertTrue(Club_Book_History.objects.filter(club=self.club, book=self.book).exists())

    def _create_club_book_history(self):
        Club_Book_History.objects.create(club=self.club, book=self.book, average_rating=5)
