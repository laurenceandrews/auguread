from clubs.models import (Book, Club, Club_Book_History, Club_Users, User,
                          User_Books)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
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
def user_favourite_books(request):
    """ View to display a list of the current user's book history. """
    user = request.user
    book_ids = User_Books.objects.filter(user=user).values_list('book', flat=True)
    books = Book.objects.filter(id__in=book_ids)
    return render(request, "partials/books_table.html",
                  {
                      'user': user,
                      'books': books,
                  })


@login_required
def user_clubs_books(request):
    """ View to display a list of the current user's book history. """
    user = request.user
    clubs_ids = Club_Users.objects.filter(user=user).exclude(role_num="1").values_list('club', flat=True)
    clubs = Club.objects.filter(id__in=clubs_ids)
    book_ids = User_Books.objects.filter(club__in=clubs).values_list('book', flat=True)
    books = Book.objects.filter(id__in=book_ids)
    return render(request, "partials/books_table.html",
                  {
                      'user': user,
                      'books': books,
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

    if role_num == "2":
        club_ids = club_users.filter(role_num="2").values_list('club', flat=True)
        clubs = Club.objects.filter(id__in=club_ids)

    if role_num == "4":
        club_ids = club_users.filter(role_num="4").values_list('club', flat=True)
        clubs = Club.objects.filter(id__in=club_ids)

    return render(request, "partials/clubs_table.html",
                  {
                      'user': user,
                      'clubs': clubs,
                  })
