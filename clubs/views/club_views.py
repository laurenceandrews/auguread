"""Views related to the clubs."""
from clubs.forms import NewClubForm
from clubs.models import Club, User
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.template.defaultfilters import slugify
from django.views.generic import ListView
from django.views.generic.list import MultipleObjectMixin
from schedule.models import Calendar, Event, Rule

from .helpers import login_prohibited, member, owner
from .mixins import (ApplicantProhibitedMixin, LoginProhibitedMixin,
                     MemberProhibitedMixin)


@login_required()
def new_club(request):
    if request.method == "POST":
        current_user = request.user
        form = NewClubForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get("name")
            city = form.cleaned_data.get("city")
            country = form.cleaned_data.get("country")
            description = form.cleaned_data.get("description")
            avg_reading_speed = form.cleaned_data.get("avg_reading_speed")
            calendar_name = form.cleaned_data.get("calendar_name")

            location = city + ", " + country

            calendar_slug = slugify(calendar_name)
            cal = Calendar(name=calendar_name, slug=calendar_slug)
            cal.save()

            meeting_type = form.cleaned_data.get("meeting_type")

            club = Club.objects.create(
                name=name,
                location=location,
                description=description,
                avg_reading_speed=avg_reading_speed,
                owner=current_user,
                calendar=cal,
                meeting_type=meeting_type
            )
            return redirect("club_list")
        else:
            return render(request, "new_club.html", {"form": form})
    else:
        return render(request, "new_club.html", {"form": NewClubForm})


class ClubListView(LoginRequiredMixin, ListView):
    """View to display a list of available clubs."""

    paginate_by = settings.NUMBER_PER_PAGE
    model = Club
    template_name = "club_list.html"
    context_object_name = "clubs"


@login_required
@member
def enter(request, club_id):
    user = request.user
    return redirect('show_user', user_id=user.id, club_id=club_id)


@login_required
def apply(request, club_id):
    user = request.user
    club = Club.objects.get(id=club_id)
    club.applied_by(user)
    return redirect('club_list')


@login_required
@owner
def approve(request, user_id, club_id):
    club = Club.objects.get(id=club_id)
    try:
        user = User.objects.get(id=user_id)
        club.accept(user)
    except ObjectDoesNotExist:
        return redirect('applicant_list', club_id=club_id)
    else:
        return redirect('show_user', user_id=user.id, club_id=club_id)



class ApplicantListView(LoginRequiredMixin, ListView, MultipleObjectMixin):
    """View that shows a list of all the applicants."""

    model = User
    template_name = "applicant_list.html"
    context_object_name = "users"
    paginate_by = settings.NUMBER_PER_PAGE

    def get_queryset(self):
        club = Club.objects.get(id=self.kwargs['club_id'])
        users = list(club.applicants.all())
        return users

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['club'] = Club.objects.get(id=self.kwargs['club_id'])
        context['user'] = self.request.user

        return context

    def post(self, request, **kwargs):
        club = Club.objects.get(id=self.kwargs['club_id'])
        emails = request.POST.getlist('check[]')
        for email in emails:
            user = User.objects.get(email=email)
            club.accept(user)
        users = club.applicants.all()
        return redirect('applicant_list', club_id=club.id)


class MemberListView(LoginRequiredMixin, ListView, MultipleObjectMixin, ApplicantProhibitedMixin):
    """View that shows a list of all the members."""

    model = User
    template_name = "member_list.html"
    context_object_name = "users"
    paginate_by = settings.NUMBER_PER_PAGE

    def get_queryset(self):
        club = Club.objects.get(id=self.kwargs['club_id'])
        users = list(club.members.all())
        return users

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['club'] = Club.objects.get(id=self.kwargs['club_id'])
        context['user'] = self.request.user

        return context

    def post(self, request, **kwargs):
        club = Club.objects.get(id=self.kwargs['club_id'])
        emails = request.POST.getlist('check[]')
        for email in emails:
            user = User.objects.get(email=email)
            club.promote(user)
        users = club.members.all()
        return redirect('member_list', club_id=club.id)


class OwnerListView(LoginRequiredMixin, ListView, MultipleObjectMixin):
    """View that shows a list of all the owners."""

    model = User
    template_name = "owner_list.html"
    context_object_name = "users"
    paginate_by = settings.NUMBER_PER_PAGE

    def get_queryset(self):
        club = Club.objects.get(id=self.kwargs['club_id'])
        users = list(club.owners.all())
        return users

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['club'] = Club.objects.get(id=self.kwargs['club_id'])
        context['user'] = self.request.user

        return context

    def post(self, request, **kwargs):
        club = Club.objects.get(id=self.kwargs['club_id'])
        emails = request.POST.getlist('check[]')
        for email in emails:
            user = User.objects.get(email=email)
            club.demote(user)
        return redirect('owner_list', club_id=club.id)


def club_recommender(request):
    """View that shows a list of all recommended clubs."""
    return render(request, 'club_recommender.html')



@login_required
@owner
def transfer(request, user_id, club_id):
    club = Club.objects.get(id=club_id)
    try:
        target = User.objects.get(id=user_id)
        club.transfer(target)
    except ObjectDoesNotExist:
        return redirect('owner_list', club_id=club_id)
    else:
        return redirect('show_user', user_id=user_id, club_id=club_id)


    form = BookRatingForm()
    return render(request, 'book_preferences.html', {'current_user': request.user, 'books_queryset': books_queryset, 'books_paginated': books_paginated, 'form': form})
