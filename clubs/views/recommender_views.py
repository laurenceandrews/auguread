"""Views related to the recommender."""
from clubs.forms import (AddressForm, LogInForm, NewClubForm, PasswordForm,
                         PostForm, SignUpForm)
#from clubs.helpers import member, owner, login_prohibited
from clubs.models import Book, Club, Club_Books, MeetingAddress, MeetingLink, Post, User, Address
from clubs.forms import ClubBookForm
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

@login_required
def RecommendationsView(request):
    """View that shows a list of all recommended books."""
    return render(request, 'rec_page.html')

def club_recommender(request):
    """View that shows a list of all recommended clubs."""
    return render(request, 'club_recommender.html')


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
