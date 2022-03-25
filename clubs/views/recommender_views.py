"""Views related to the recommender."""
from clubs.forms import ClubRecommenderForm
# from clubs.helpers import member, owner
from django.conf import settings
from statistics import mean

from clubs.book_to_user_recommender.book_to_user import BookToUserRecommender
from clubs.club_to_user_recommender.club_to_user_recommender import ClubUserRecommender
from clubs.forms import (AddressForm, BookRatingForm, CalendarPickerForm,
                         ClubBookForm, CreateEventForm, LogInForm,
                         MeetingAddressForm, MeetingLinkForm, NewClubForm,
                         PasswordForm, PostForm, SignUpForm)
# from clubs.helpers import member, owner
from clubs.models import (Address, Book, Book_Rating, Club, Club_Book_History,
                          Club_Books, Club_Users, MeetingAddress, MeetingLink,
                          Post, User)

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
from django.urls import reverse
from django.views import View
from django.db.models import Q
from clubs.club_to_user_recommender.club_to_user_recommender import ClubUserRecommender

@login_required
def RecommendationsView(request):
    """View that shows a list of all recommended books."""
    return render(request, 'rec_page.html')

class ClubRecommenderView(LoginRequiredMixin, View):
    """View that handles the club recommendations."""
    http_method_names = ['get', 'post']

    def get(self, request):
        """Display template."""
        user_id = self.request.user.id

        club_ids_in_person = ClubUserRecommender(user_id).get_best_clubs_in_person()
        club_ids_online = ClubUserRecommender(user_id).get_best_clubs_online()
        self.club_recs_in_person = Club.objects.filter(id__in = club_ids_in_person)[0:11]
        self.club_recs_online = Club.objects.filter(id__in  = club_ids_online)[0:11]

        # get all the clubs and sort alphabetcally
        self.clubs_queryset = Club.objects.all().order_by('name')

        # query the list of clubs by name or location
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

    # def form_valid(self, form):
    #     user = User.objects.get(id = self.kwargs['id'])
    #     club = form.cleaned_data.get('club')
    #     return render(self.request, 'club_recommender.html')
    
    # def get_data(self, **kwargs):  
    #     data = super().get_data(**kwargs)
    #     user = User.objects.get(id = self.kwargs['id'])
    #     data['first_name'] = user.first_name

    def render(self):
        """Render template with blank form."""

        return render(
            self.request, 'club_recommender.html',
            {
                'next': self.next,
                'clubs_paginated': self.clubs_paginated,
                'club_recs_in_person': self.club_recs_in_person,
                'club_recs_online': self.club_recs_online
            }
        )


class ClubBookSelectionView(LoginRequiredMixin, View):
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

        lastBookRead = Club_Book_History.objects.last()
        if lastBookRead:

            # Verify applicant number below
            club_users = Club_Users.objects.filter(club=club).exclude(role_num=1).values('user')
            book_ratings = Book_Rating.objects.filter(book=lastBookRead.book, user__in=club_users)
            all_ratings = map(int, list(book_ratings.values_list('rating', flat=True)))
            average_rating = mean(all_ratings)

            lastBookRead.average_rating = average_rating

            if lastBookRead.average_rating >= 6:
                Club_Books.objects.create(
                    club=club,
                    book=lastBookRead.book
                )

        Club_Book_History.objects.create(
            club=club,
            book=book,
            average_rating=1
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

        # returns the collaborative filtering of ratings between users
        # user_rec_book_ids = BookToUserRecommender().get_collaborative_filtering()
        # self.user_rec_books = Book.objects.filter(id__in=user_rec_book_ids)[0:11]

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
                      {
                          # 'user_rec_books_exists': self.user_rec_books.exists(),
                          # 'user_rec_books': self.user_rec_books,
                          'club_favourites_exist': self.club_favourites_exist,
                          'club_favourites': self.club_favourites}
                      )
