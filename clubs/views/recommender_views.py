"""Views related to the recommender."""
from clubs.forms import (AddressForm, LogInForm, NewClubForm, PasswordForm,
                         PostForm, SignUpForm, BookRatingForm)
# from clubs.helpers import member, owner
from clubs.models import Book, Club, MeetingAddress, MeetingLink, Post, User, Address
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import (Http404, HttpResponse, HttpResponseForbidden,
                         HttpResponseRedirect)
from django.shortcuts import redirect, render
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.views import View
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)
from django.views.generic.list import MultipleObjectMixin
from schedule.models import Calendar, Event, Rule

from clubs.forms import (CalendarPickerForm, CreateEventForm, MeetingAddressForm,
                    MeetingLinkForm, SignUpForm)
# from clubs.helpers import login_prohibited

@login_required
def RecommendationsView(request):
    """View that shows a list of all recommended books."""
    return render(request, 'rec_page.html')

def club_recommender(request):
    """View that shows a list of all recommended clubs."""
    clubs_queryset = Club.objects.all()

    paginator = Paginator(clubs_queryset, settings.CLUBS_PER_PAGE)
    page_number = request.GET.get('page')
    clubs_paginated = paginator.get_page(page_number)

    return render(request, 'club_recommender.html', {'current_user': request.user, 'clubs_queryset': clubs_queryset, 'clubs_paginated': clubs_paginated})


def book_preferences(request):
    """View that allows the user to view all books and rate them."""
    books_queryset = Book.objects.all()

    paginator = Paginator(books_queryset, settings.BOOKS_PER_PAGE)
    page_number = request.GET.get('page')
    books_paginated = paginator.get_page(page_number)

    return render(request, 'book_preferences.html', {'current_user': request.user, 'books_queryset': books_queryset, 'books_paginated': books_paginated})

class BookPreferencesView(LoginRequiredMixin, View):
    """View that handles book preferences."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = 'book_preferences'

    books_queryset = Book.objects.all()
    paginator = Paginator(books_queryset, settings.BOOKS_PER_PAGE)

    def get(self, request):
        """Display log in template."""

        page_number = request.GET.get('page')
        books_paginated = self.paginator.get_page(page_number)

        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handles submit attempt."""

        form = BookRatingForm(request.POST)
        self.next = request.POST.get('next') or settings.AUTO_REDIRECT_URL

        return self.render()

    def render(self):
        """Render template with blank form."""

        form = BookRatingForm()
        return render(self.request, 'book_preferences.html', {'form': form, 'next': self.next})

class ClubRecommenderView(LoginRequiredMixin, View):
    """View that handles the club recommendations."""
    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = 'club_recommender'



    def get(self, request):
        self.clubs_queryset = Club.objects.all().order_by('name')

        paginator = Paginator(self.clubs_queryset, settings.CLUBS_PER_PAGE)

        page_number = request.GET.get('page')
        self.clubs_paginated = paginator.get_page(page_number)

        self.next = request.GET.get('next') or ''
        return self.render()

    def render(self):
        """Render template with blank form."""

        return render(self.request, 'club_recommender.html', {'next':self.next, 'clubs_paginated': self.clubs_paginated})

