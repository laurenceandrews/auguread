from clubs.forms import ClubBookForm
from clubs.models import Book, BookRatingForm, Club, Club_Books
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.edit import CreateView

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
    #redirect_when_submitted = 'book_preferences'

    def get(self, request):
        """Display template."""

        self.books_queryset = Book.objects.all()
        self.paginator = Paginator(self.books_queryset, settings.BOOKS_PER_PAGE)
        self.page_number = request.GET.get('page')
        self.books_paginated = self.paginator.get_page(self.page_number)

        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handles submit attempt."""

        form = BookRatingForm(request.POST)
        self.next = request.POST.get('next') or settings.AUTO_REDIRECT_URL
        rating = form.rating
        # if rating is not None:
        # Check if there is already a Book_Rating for this book
        # If so, overwrite it
        # Otherwise, create a new one

        return self.render()

    def render(self):
        """Render template with blank form."""

        form = BookRatingForm()
        return render(self.request, 'book_preferences.html', {'form': form, 'next': self.next, 'books_paginated': self.books_paginated})


class ClubBookSelectionView(CreateView):
    """Class-based generic view for new post handling."""

    model = Club_Books
    template_name = 'club_book_select.html'
    form_class = ClubBookForm

    def get_form_kwargs(self):
        kwargs = super(ClubBookSelectionView, self).get_form_kwargs()
        kwargs['club_id'] = self.kwargs['club_id']
        return kwargs

    def form_valid(self, form):
        """Process a valid form."""
        club = Club.objects.get(id=self.kwargs['club_id'])

        book = form.cleaned_data.get('book')

        club_book = Club_Books.objects.create(
            club=club,
            book=book
        )
        return render(self.request, 'home.html')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        club = Club.objects.get(id=self.kwargs['club_id'])
        context['club_name'] = club.name

        return context

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        return redirect('home')
