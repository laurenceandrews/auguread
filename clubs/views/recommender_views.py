"""Views related to the recommender."""
from statistics import mean

from clubs.book_to_club_recommender.book_to_club_recommender_age import \
    ClubBookAgeRecommender
from clubs.book_to_club_recommender.book_to_club_recommender_author import \
    ClubBookAuthorRecommender
from clubs.book_to_user_recommender.book_to_user_knn import \
    BookToUserRecommender
from clubs.club_to_user_recommender.club_to_user_recommender import \
    ClubUserRecommender
from clubs.models import (Book, Book_Rating, Club, Club_Book_History,
                          Club_Books, Club_Users, ClubBookRecommendation,
                          User_Books, UserBookRecommendation,
                          UserClubRecommendation)
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


class ClubRecommenderView(LoginRequiredMixin, View):
    """View that handles the club recommendations."""
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        """Display template."""

        self.user = request.user
        user_id = self.user.id

        # get the user's club recommendations
        user_club_recommendations = UserClubRecommendation.objects.filter(user=self.user).order_by()
        print(user_club_recommendations)
        if user_club_recommendations.exists():
            club_ids = UserClubRecommendation.objects.filter(user=self.user).values_list('club', flat=True)
            clubs = Club.objects.filter(id__in=club_ids)
        else:
            # populate databse
            club_ids_in_person = ClubUserRecommender(self.user.id).get_best_clubs_in_person_list()
            club_ids_online = ClubUserRecommender(self.user.id).get_best_clubs_online_list()

            club_ids = []
            club_ids = club_ids_in_person + club_ids_online

            clubs = Club.objects.filter(id__in=club_ids)

            for club in clubs:
                UserClubRecommendation.objects.create(user=self.user, club=club)

        # filter by meeting type
        query = self.request.GET.get('q')
        if query:
            clubs = clubs.filter(
                Q(meeting_type__icontains=query) | Q(location__icontains=query)
            ).distinct()

        self.clubs_queryset = clubs.distinct().order_by('name')

        paginator = Paginator(self.clubs_queryset, settings.CLUBS_PER_PAGE)
        page_number = request.GET.get('page')
        self.clubs_paginated = paginator.get_page(page_number)

        self.next = request.GET.get('next') or ''
        return self.render()

    def render(self):
        """Render template with blank form."""

        return render(
            self.request, 'club_recommender.html',
            {
                'next': self.next,
                'clubs_paginated': self.clubs_paginated,
                'user': self.user
            }
        )


class RecommendedClubBookListView(LoginRequiredMixin, View):
    """View to display a list of recommended books for clubs."""

    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        """Display template."""

        club_id = self.kwargs['club_id']
        self.club = Club.objects.get(id=club_id)

        # get the club's book recommendations
        club_book_recommendations = ClubBookRecommendation.objects.filter(club=self.club)
        if club_book_recommendations.exists():
            book_ids = ClubBookRecommendation.objects.filter(club=self.club).values_list('book', flat=True)
            books = Book.objects.filter(id__in=book_ids)
        else:
            # populate databse
            book_ids = ClubBookAgeRecommender(self.club.id).get_recommended_books()

            if not ClubBookAuthorRecommender(self.club.id).author_books_is_empty():
                book_ids_from_author_rec = ClubBookAuthorRecommender(self.club.id).get_recommended_books()
                if(len(book_ids_from_author_rec) > len(book_ids)):
                    book_ids = book_ids_from_author_rec
                books = Book.objects.filter(id__in=book_ids)
            else:
                books = Book.objects.filter(id__in=book_ids)

            for book in books:
                ClubBookRecommendation.objects.create(club=self.club, book=book)

        self.books = books.distinct()

        paginator = Paginator(books, settings.NUMBER_PER_PAGE)
        page_number = request.GET.get('page')
        self.page_obj = paginator.get_page(page_number)

        return self.render()

    def render(self):
        """Render template."""

        return render(self.request, 'recommended_books_for_club_list.html', {
            'books': self.books,
            'club': self.club,
            'page_obj': self.page_obj
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
        user_rec_books = UserBookRecommendation.objects.filter(user=current_user)
        if user_rec_books.exists():
            user_rec_books_ids = UserBookRecommendation.objects.filter(user=current_user).values_list('book', flat=True)
            self.user_rec_books = Book.objects.filter(id__in=user_rec_books_ids)
        else:
            # populate the databse
            user_rec_books_ids = BookToUserRecommender(user_id_to_query=current_user.id).build_dictionary()
            self.user_rec_books = Book.objects.filter(id__in=user_rec_books_ids)
            for book in self.user_rec_books:
                UserBookRecommendation.objects.create(book=book, user=current_user)

        club_favourites = Club_Books.objects.exclude(club__in=current_user.clubs_attended()).order_by('-id')
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
                          'club_favourites_exist': self.club_favourites.exists(),
                          'club_favourites': self.club_favourites,
                          'friends_favourites_exists': self.user_favourites.exists(),
                          'friends_favourites': self.user_favourites
                      }
                      )
