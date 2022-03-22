from clubs.forms import (BookRatingForm, ClubBookHistoryForm,
                         UserBookHistoryForm, UserBooksForm)
from clubs.models import (Book, Book_Rating, Club, Club_Book_History, User,
                          User_Book_History, User_Books)
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView

from .helpers import login_prohibited
from .mixins import (ApplicantProhibitedMixin, LoginProhibitedMixin,
                     MemberProhibitedMixin)


class BookDetailView(DetailView):

    model = Book
    template_name = 'book_detail.html'
    pk_url_kwarg = "book_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        book = Book.objects.get(id=self.kwargs['book_id'])

        rating_exists = Book_Rating.objects.filter(user=self.request.user, book=book).exists()
        context['rating_exists'] = rating_exists
        if rating_exists:
            context['book_rating'] = Book_Rating.objects.get(user=self.request.user, book=book).rating

        context['book_rating_form'] = BookRatingForm()

        user_book_history_exists = User_Book_History.objects.filter(user=user, book=book).exists()
        context['user_book_history_exists'] = user_book_history_exists
        context['user_book_history_form'] = UserBookHistoryForm()

        user_books_exists = User_Books.objects.filter(user=user, book=book).exists()
        context['user_books_exists'] = user_books_exists
        context['user_book_form'] = UserBooksForm()

        return context

    def get(self, request, *args, **kwargs):
        """Handle get request, and redirect to user_list if book_id invalid."""

        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect('rec')


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


class CreateBookRatingView(CreateView):
    model = Book_Rating
    template_name = 'book_rating_create.html'
    form_class = BookRatingForm

    def form_valid(self, form):
        """Process a valid form."""
        current_user = self.request.user
        book = Book.objects.get(id=self.kwargs['book_id'])
        rating = self.request.POST.get('rating')

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

        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        return reverse('book_preferences')


class CreateClubBookHistoryView(CreateView):
    model = Club_Book_History
    template_name = 'club_book_history_create.html'
    form_class = ClubBookHistoryForm

    def form_valid(self, form):
        """Process a valid form."""
        current_user = self.request.user
        club = Club.objects.get(id=self.kwargs['club_id'])
        book = Book.objects.get(id=self.kwargs['book_id'])

        club_book_history_exists = Club_Book_History.objects.filter(club=club, book=book)

        if club_book_history_exists.exists():
            club_book_history = Club_Book_History.objects.get(club=club, book=book)
            club_book_history.delete()

        club_book_history = Club_Book_History.objects.create(
            club=club,
            book=book
        )
        messages.add_message(self.request, messages.SUCCESS, "Book set as club's currently reading!")

        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))


class CreateUserBookHistoryView(LoginRequiredMixin, CreateView):
    model = User_Book_History
    template_name = 'user_book_history_create.html'
    form_class = UserBookHistoryForm

    def form_valid(self, form):
        """Process a valid form."""
        try:
            user = User.objects.get(id=self.kwargs['user_id'])
            book = Book.objects.get(id=self.kwargs['book_id'])
        except ObjectDoesNotExist:
            messages.add_message(self.request, messages.ERROR, "Invalid user or book!")
            return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

        user_book_history_exists = User_Book_History.objects.filter(user=user, book=book)

        if user_book_history_exists.exists():
            user_book_history_object = User_Book_History.objects.get(user=user, book=book)
            user_book_history_object.delete()

        user_book_history_object = User_Book_History.objects.create(
            user=user,
            book=book
        )
        messages.add_message(self.request, messages.SUCCESS, "Book set as your currently reading!")

        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))


class CreateUserBooksView(LoginRequiredMixin, CreateView):
    model = User_Books
    template_name = 'user_books_create.html'
    form_class = UserBooksForm

    def form_valid(self, form):
        """Process a valid form."""
        try:
            user = User.objects.get(id=self.kwargs['user_id'])
            book = Book.objects.get(id=self.kwargs['book_id'])
        except ObjectDoesNotExist:
            messages.add_message(self.request, messages.ERROR, "Invalid user or book!")
            return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

        user_books_exists = User_Books.objects.filter(user=user, book=book)

        if user_books_exists.exists():
            messages.add_message(self.request, messages.SUCCESS, "Book is already one of your favourites!")
            return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

        user_books_object = User_Books.objects.create(
            user=user,
            book=book
        )
        messages.add_message(self.request, messages.SUCCESS, "Book set as one of your favourites!")

        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))


@login_required
def delete_user_book_favourite(request, user_id, book_id):
    """ View that handles user book delete requests. """
    try:
        user = User.objects.get(id=user_id)
        book = Book.objects.get(id=book_id)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "Invalid user or book!")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    user_books_exists = User_Books.objects.filter(user=user, book=book).exists()
    if user_books_exists:
        user_book = User_Books.objects.get(user=user, book=book)
        user_book.delete()
        messages.add_message(request, messages.SUCCESS, "Book removed from your favourites!")
    else:
        messages.add_message(request, messages.SUCCESS, "This book was not found in your favourites!")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
