from clubs.forms import BookRatingForm
from clubs.models import Book, Club, Club_Books, Book_Rating
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic.edit import CreateView
from django.db.models import Q

from .helpers import login_prohibited
from .mixins import (ApplicantProhibitedMixin, LoginProhibitedMixin,
                     MemberProhibitedMixin)


@login_required
def RecommendationsView(request):
    """View that shows a list of all recommended books."""
    return render(request, 'rec_page.html')


class BookPreferencesView(LoginRequiredMixin, View):
    """View that handles book preferences."""

    http_method_names = ['get', 'post']

    def get(self, request):
        """Display template."""

        self.books_queryset = Book.objects.all().order_by('title')
        query = request.GET.get('q')
        if query:
            self.books_queryset = Book.objects.filter(
                Q(title__icontains=query) | Q(author__icontains=query)
            ).distinct()

        paginator = Paginator(self.books_queryset, settings.BOOKS_PER_PAGE)
        page_number = request.GET.get('page')
        self.books_paginated = paginator.get_page(page_number)

        self.innerForm = BookRatingForm()

        self.next = request.GET.get('next') or ''
        return self.render()

    def render(self):
        """Render template."""

        return render(self.request, 'book_preferences.html', {'innerForm': self.innerForm, 'next': self.next, 'books_paginated': self.books_paginated})


def rate_book(request, book_id):
    current_user = request.user
    book = Book.objects.get(id=book_id)
    rating = request.POST.get('rating')

    print(book.title)

    book_rating_exists = Book_Rating.objects.filter(user=current_user, book=book)

    if book_rating_exists.exists():
        book_rating = Book_Rating.objects.get(
            user=current_user,
            book=book
        )
        book_rating.rating = rating
        book_rating.save()
        messages.add_message(request, messages.SUCCESS, "Book rating updated!")
    else:
        book_rating = Book_Rating.objects.create(
            user=current_user,
            book=book,
            rating=rating
        )
        messages.add_message(request, messages.SUCCESS, "Book rating created!")

    return redirect('book_preferences')

class CreateBookRatingView(CreateView):
    model = Book_Rating
    template_name = 'book_rating_create.html'
    form_class = BookRatingForm

    def form_valid(self, form):
        """Process a valid form."""
        current_user = self.request.user
        book = Book.objects.get(id=self.kwargs['book_id'])
        rating = self.request.POST.get('rating')

        print(book.title)

        book_rating_exists = Book_Rating.objects.filter(user=current_user, book=book)

        if book_rating_exists.exists():
            book_rating = Book_Rating.objects.get(
                user=current_user,
                book=book
            )
            book_rating.rating = rating
            book_rating.save()
            messages.add_message(self.request, messages.SUCCESS, "Book rating updated!")
        else:
            book_rating = Book_Rating.objects.create(
                user=current_user,
                book=book,
                rating=rating
            )
            messages.add_message(self.request, messages.SUCCESS, "Book rating created!")

        return redirect('book_preferences')

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        return reverse('book_preferences')
