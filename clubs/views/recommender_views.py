"""Views related to the recommender."""
from statistics import mean

from clubs.book_to_club_recommender.book_to_club_recommender_age import \
    ClubBookAgeRecommender
from clubs.book_to_club_recommender.book_to_club_recommender_author import \
    ClubBookAuthorRecommender
from clubs.book_to_user_recommender.book_to_user import BookToUserRecommender
from clubs.club_to_user_recommender.club_to_user_recommender import \
    ClubUserRecommender
from clubs.forms import (AddressForm, BookRatingForm, CalendarPickerForm,
                         ClubRecommenderForm, CreateEventForm, LogInForm,
                         MeetingAddressForm, MeetingLinkForm, NewClubForm,
                         PasswordForm, PostForm, SignUpForm)
from clubs.models import (Address, Book, Book_Rating, Club, Club_Book_History,
                          Club_Books, Club_Users, MeetingAddress, MeetingLink,
                          Post, User, User_Book_History, User_Books)
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


class ClubRecommenderView(TenPosRatingsRequiredMixin, View):
    """View that handles the club recommendations."""
    http_method_names = ['get', 'post']

    def get(self, request):
        """Display template."""
        user_id = self.request.user.id

        club_ids_in_person = ClubUserRecommender(user_id).get_best_clubs_in_person()
        # club_ids_online = ClubUserRecommender(user_id).get_best_clubs_online()
        self.club_recs_in_person = Club.objects.filter(id__in=club_ids_in_person)
        # self.club_recs_online = Club.objects.filter(id__in  = club_ids_online)

        # get all the clubs and sort alphabetcally
        self.clubs_queryset = Club.objects.all().order_by('name')

        # query the list of clubs by name or location
        query = request.GET.get('q')
        if query:
            self.clubs_queryset = Club.objects.filter(
                Q(name__icontains=query) | Q(location__icontains=query)
            ).distinct()

        paginator = Paginator(self.club_recs_in_person, settings.CLUBS_PER_PAGE)
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
                'club_recs_in_person': self.club_recs_in_person
                # 'club_recs_online': self.club_recs_online
            }
        )


class RecommendedClubBookListView(LoginRequiredMixin, View):
    """View to display a list of recommended books for clubs."""

    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        """Display template."""

        club_id = self.kwargs['club_id']
        self.club = Club.objects.get(id=club_id)

        if not ClubBookAuthorRecommender(club_id).author_books_is_empty():
            book_ids = ClubBookAuthorRecommender(club_id).get_recommended_books()
            if(len(book_ids) < 6):
                book_ids = ClubBookAgeRecommender(club_id).get_recommended_books()
        else:
            book_ids = ClubBookAgeRecommender(club_id).get_recommended_books()

        self.books = Book.objects.filter(id__in=book_ids)

        return self.render()

    def render(self):
        """Render template."""

        return render(self.request, 'recommended_books_for_club_list.html', {
            'books': self.books,
            'club': self.club
        })


@login_required
def club_book_select_view(request, club_id, book_id):
    """Handles selecting a book for a club."""

    try:
        club = Club.objects.get(id=club_id)
        book = Book.objects.get(id=book_id)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "Invalid club or book!")
        return redirect('rec')

    lastBookRead = Club_Book_History.objects.last()
    if lastBookRead:
        club_users = Club_Users.objects.filter(club=club).exclude(role_num=1).values('user')
        book_ratings = Book_Rating.objects.filter(book=lastBookRead.book, user__in=club_users)
        if book_ratings.exists():
            all_ratings = map(int, list(book_ratings.values_list('rating', flat=True)))
            average_rating = mean(all_ratings)
        else:
            average_rating = 0

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

    messages.add_message(request, messages.SUCCESS, f"{book.title} selected!")
    return redirect('club_detail', club.id)


class RecommendationsView(LoginRequiredMixin, View):
    """View that handles the book recommendations."""

    http_method_names = ['get', 'post']

    def get(self, request):
        """Display template."""
        current_user = self.request.user

        # returns the collaborative filtering of ratings between users
        user_rec_book_ids = BookToUserRecommender().get_collaborative_filtering()
        self.user_rec_books = Book.objects.filter(id__in=user_rec_book_ids)[0:15]

        club_favourites = Club_Books.objects.exclude(club__in=current_user.clubs_attended()).order_by('-id')

        if club_favourites.count() == 0:
            self.club_favourites_exist = False
        else:
            self.club_favourites_exist = True

        self.club_favourites_book_ids = club_favourites.values('book')[0:15]
        self.club_favourites = Book.objects.filter(id__in=self.club_favourites_book_ids)

        user_favourites = User_Books.objects.filter(user__in=current_user.friends_list()).order_by('-id')

        self.user_favourites_book_ids = user_favourites.values('book')[0:15]
        self.user_favourites = Book.objects.filter(id__in=self.user_favourites_book_ids)

        return self.render()

    def render(self):
        """Render template."""

        return render(self.request, 'rec_page.html',
                      {
                          'user_rec_books_exists': self.user_rec_books.exists(),
                          'user_rec_books': self.user_rec_books,
                          'club_favourites_exist': self.club_favourites_exist,
                          'club_favourites': self.club_favourites,
                          'friends_favourites_exists': self.user_favourites.exists(),
                          'friends_favourites': self.user_favourites
                      }
                      )
