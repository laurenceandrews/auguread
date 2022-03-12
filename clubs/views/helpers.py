from clubs.models import Club
from django.conf import settings
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
        club = Club.objects.get(id=kwargs['club_id'])
        if (request.user in club.members.all() or request.user in club.owners.all()
                or club.owner.email == request.user.email):
            return view_function(request, *args, **kwargs)
        else:
            return redirect(settings.AUTO_REDIRECT_URL)

    return modified_view_function


"""Specifies view that only owners can access"""


def owner(view_function, *args, **kwargs):
    def modified_view_function(request, *args, **kwargs):
        club = Club.objects.get(id=kwargs['club_id'])
        if request.user in club.owner.all() or club.owner.email == request.user.email:
            return view_function(request, *args, **kwargs)
        else:
            return redirect(settings.AUTO_REDIRECT_URL)

    return modified_view_function
