"""Tests of the book_detail view."""


from clubs.models import Book, Book_Rating, Club, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse
from schedule.models import Calendar, Event, Rule


class BookDetailViewTest(TestCase):
    """Tests of the book_detail view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_book.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self.book = Book.objects.get(pk=20)
        Book_Rating.objects.create(book=self.book, user=self.user, rating=1)

        self.url = reverse(
            'book_detail', kwargs={'book_id': self.book.id}
        )

    def test_book_detail_url(self):
        self.assertEqual(self.url, f'/book/detail/{self.book.id}/')

    def test_get_book_detail_with_valid_id(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_detail.html')
        book = response.context['book']
        self.assertEquals(book, self.book)
        self.assertEquals(Book_Rating.objects.filter(book=book, user=self.user).exists(), True)
        self.assertContains(response,
                            '            <button type="submit" class="justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">Change your rating</button>',
                            status_code=200)

    def test_get_book_detail_wihere_no_rating_exists(self):
        self.client.login(email=self.user.email, password="Password123")
        new_book = Book.objects.create(
            ISBN="9781904605287",
            title="The Third ManThe Third Man",
            author="Graham Greene ",
            publication_year="1950",
            publisher="CSA WORD")
        self.url = reverse(
            'book_detail', kwargs={'book_id': new_book.id}
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_detail.html')
        book = response.context['book']
        self.assertEquals(book, new_book)
        self.assertNotEquals(Book_Rating.objects.filter(book=book, user=self.user).exists(), True)
        self.assertContains(response,
                            '<button type="submit" class="justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">Rate book</button>',
                            status_code=200)

    def test_get_book_detail_with_invalid_id(self):
        self.client.login(email=self.user.email, password="Password123")
        url = reverse('book_detail', kwargs={'book_id': 0})
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed(response, 'rec_page.html')

    def test_get_book_detail_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
