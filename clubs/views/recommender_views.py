"""Views related to the recommender."""
from clubs.forms import (AddressForm, BookRatingForm, CalendarPickerForm,
                         ClubBookForm, CreateEventForm, LogInForm,
                         MeetingAddressForm, MeetingLinkForm, NewClubForm,
                         PasswordForm, PostForm, SignUpForm)
# from clubs.helpers import member, owner
from clubs.models import (Address, Book, Club, Club_Book_History, Club_Books,
                          MeetingAddress, MeetingLink, Post, User)
from clubs.views.club_views import MemberListView
from clubs.views.mixins import TenPosRatingsRequiredMixin
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q
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


class ClubRecommenderView(LoginRequiredMixin, View):
    """View that handles the club recommendations."""

    http_method_names = ['get', 'post']

    def get(self, request):
        """Display template."""

        self.clubs_queryset = Club.objects.all().order_by('name')
        query = request.GET.get('q')
        if query:
            self.clubs_queryset = Club.objects.filter(
                Q(name__icontains=query) | Q(location__icontains=query)
            ).distinct()

        paginator = Paginator(self.clubs_queryset, settings.CLUBS_PER_PAGE)
        page_number = request.GET.get('page')
        self.clubs_paginated = paginator.get_page(page_number)

        self.next = request.GET.get('next') or ''
        return self.render()

    def render(self):
        """Render template with blank form."""

        return render(self.request, 'club_recommender.html', {'next': self.next, 'clubs_paginated': self.clubs_paginated})


class ClubBookSelectionView(LoginRequiredMixin, CreateView):
    """Class-based generic view for club book selection handling."""

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

        Club_Book_History.objects.create(
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
        """Return URL to redirect the user to after valid form handling."""
        return redirect('home')


class RecommendationsView(LoginRequiredMixin, View):
    """View that handles the club recommendations."""
    http_method_names = ['get', 'post']

    def get(self, request):
        """Display template."""

        club_favourites = Club_Books.objects.all()
        if club_favourites.count() == 0:
            self.club_favourites_exist = False
        else:
            self.club_favourites_exist = True

        self.club_favourites_book_ids = Club_Books.objects.values('book')[0:11]
        self.club_favourites = Book.objects.filter(id__in=self.club_favourites_book_ids)

        return self.render()

    def render(self):
        """Render template."""

        return render(self.request, 'rec_page.html',
                      {'club_favourites_exist': self.club_favourites_exist, 'club_favourites': self.club_favourites}
                      )
