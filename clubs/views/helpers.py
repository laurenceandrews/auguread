from clubs.models import Club, Club_Users
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect


def login_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)
    return modified_view_function


"""Specifies view that only members can access"""


def member(view_function, *args, **kwargs):
    def modified_view_function(request, *args, **kwargs):
        redirect_when_is_applicant_url = 'club_list'

        club = Club.objects.get(id=kwargs['club_id'])
        user = request.user
        if Club_Users.objects.filter(club=club, user=user).exists():
            if Club_Users.objects.get(club=club, user=user).role_num == 1:
                messages.add_message(request, messages.ERROR, "Club applicants cannot perform this action!")
                return redirect(redirect_when_is_applicant_url)
            else:
                return view_function(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, "You are not in this club!")
            return redirect(redirect_when_is_applicant_url)

    return modified_view_function


"""Specifies view that only owners can access"""


def owner(view_function, *args, **kwargs):
    def modified_view_function(request, *args, **kwargs):
        redirect_when_is_not_owner_url = 'club_list'

        club = Club.objects.get(id=kwargs['club_id'])
        user = request.user
        if Club_Users.objects.filter(club=club, user=user).exists():
            if Club_Users.objects.get(club=club, user=user).role_num == 4:
                return view_function(request, *args, **kwargs)
            else:
                messages.add_message(request, messages.ERROR, "Only club owners can perform this action!")
                return redirect(redirect_when_is_not_owner_url)
        else:
            messages.add_message(request, messages.ERROR, "You are not in this club!")
            return redirect(redirect_when_is_not_owner_url)

    return modified_view_function
