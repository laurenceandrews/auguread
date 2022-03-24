from clubs.models import (Book, Club, Club_Book_History, Club_Books,
                          Club_Users, User, User_Book_History, User_Books)
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views import View

from .helpers import login_prohibited
from .mixins import (ApplicantProhibitedMixin, LoginProhibitedMixin,
                     MemberProhibitedMixin)


class UserSummaryView(LoginRequiredMixin, View):
    """View that renders a page of summary information about the user."""
    http_method_names = ['get', 'post']

    def get(self, request):
        """Display template."""

        return self.render()

    def render(self):
        """Render template."""

        return render(self.request, 'user_summary.html')


@login_required
def user_current_book(request):
    """ View to display the current user's current book. """
    user = request.user
    user_book_history_exists = User_Book_History.objects.filter(user=user).exists()
    if user_book_history_exists:
        current_book = User_Book_History.objects.filter(user=user).last().book

        return render(request, "partials/books_table.html",
                      {
                          'user': user,
                          'books': [current_book],
                          'single_book': True,
                      })
    else:
        return render(request, "partials/books_table.html",
                      {
                          'user': user,
                          'single_book': True,
                      })


@login_required
def user_favourite_books(request):
    """ View to display a list of the current user's book history. """
    user = request.user
    book_ids = User_Books.objects.filter(user=user).values_list('book', flat=True)
    books = Book.objects.filter(id__in=book_ids)

    query = request.GET.get('q')
    if query:
        books = books.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        ).distinct()

    return render(request, "partials/books_table.html",
                  {
                      'user': user,
                      'books': books
                  })


@login_required
def user_clubs_books(request):
    """ View to display a list of the current user's club's currently reading. """
    user = request.user
    clubs_ids = Club_Users.objects.filter(user=user).exclude(role_num="1").values_list('club', flat=True)
    clubs = Club.objects.filter(id__in=clubs_ids)
    book_ids = []
    for club in clubs:
        if club.currently_reading() is not None:
            book_ids.append(club.currently_reading().id)
    books = Book.objects.filter(id__in=book_ids)

    query = request.GET.get('q')
    if query:
        books = books.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        ).distinct()

    return render(request, "partials/books_table.html",
                  {
                      'user': user,
                      'books': books
                  })


@login_required
def clubs_list(request, role_num):
    """ View to display a list of the current user's clubs based on the role_num. """
    user = request.user
    club_users = Club_Users.objects.filter(user=user)
    club_ids = Club_Users.objects.filter(user=user).exclude(role_num="1").values_list('club', flat=True)
    clubs = Club.objects.filter(id__in=club_ids)
    if role_num == "1":
        club_ids = club_users.filter(role_num="1").values_list('club', flat=True)
        clubs = Club.objects.filter(id__in=club_ids)

    elif role_num == "2":
        club_ids = club_users.filter(role_num="2").values_list('club', flat=True)
        clubs = Club.objects.filter(id__in=club_ids)

    elif role_num == "4":
        club_ids = club_users.filter(role_num="4").values_list('club', flat=True)
        clubs = Club.objects.filter(id__in=club_ids)

    else:
        clubs = Club.objects.none()

    query = request.GET.get('q')
    if query:
        clubs = clubs.filter(
            Q(name__icontains=query) | Q(location__icontains=query)
        ).distinct()

    paginator = Paginator(clubs, settings.NUMBER_PER_PAGE)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "summary_clubs_table.html",
                  {
                      'user': user,
                      'clubs': clubs,
                      'role_num': role_num,
                      'page_obj': page_obj
                  })
