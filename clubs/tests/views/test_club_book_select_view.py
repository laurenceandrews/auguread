"""Unit tests for the club book select page."""
from clubs.forms import ClubBookForm
from clubs.models import Book, Club, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse
from schedule.models import Calendar


class ClubBookSelectViewTest(TestCase):

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
        self.club = Club.objects.get(pk=6)

        self.url = reverse('club_book_select', kwargs={'club_id': self.club.id})

        self.book = Book.objects.get(pk=20)

        self.form_input = {
            'book': self.book
        }

    def test_club_book_select_url(self):
        self.assertEqual(self.url, f'/club/book/edit/{self.club.id}/')

    def test_get_club_book_select_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    
    def test_get_club_book_select(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_book_select.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ClubBookForm))
        self.assertFalse(form.is_bound)
    
    def test_unsuccesful_calendar_picker(self):
        self.client.login(email=self.user.email, password="Password123")
        self.form_input['book'] = 'BAD_BOOK'
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_book_select.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ClubBookForm))
        self.assertTrue(form.is_bound)
