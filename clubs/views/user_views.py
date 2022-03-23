"""Views related to all types of users"""
from clubs.forms import LogInForm, PasswordForm, SignUpForm, UserDeleteForm
from clubs.models import Club, User
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import FormView
from django.views.generic.list import MultipleObjectMixin

from .helpers import login_prohibited
from .mixins import (ApplicantProhibitedMixin, LoginProhibitedMixin,
                     MemberProhibitedMixin)


class UserListView(LoginRequiredMixin, ListView, MultipleObjectMixin, ApplicantProhibitedMixin):
    """View that shows a list of all users"""
    model = User
    template_name = "user_list.html"
    context_object_name = "users"
    paginate_by = settings.NUMBER_PER_PAGE

    def get_queryset(self):
        club = Club.objects.get(id=self.kwargs['club_id'])
        users = list(club.members()) + list(club.officers()) + list(club.owners())
        return users

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        club = Club.objects.get(id=self.kwargs['club_id'])
        context['club'] = club
        context['user'] = self.request.user

        return context


@login_required
def user_detail(request):
    user = request.user
    return render(request, 'user_detail.html', {'target': user})


class ApplicantListView(LoginRequiredMixin, ListView, MultipleObjectMixin):
    """View that shows a list of all the applicants."""

    model = User
    template_name = "applicant_list.html"
    context_object_name = "users"
    paginate_by = settings.NUMBER_PER_PAGE

    def get_queryset(self):
        club = Club.objects.get(id=self.kwargs['club_id'])
        users = club.applicants()
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
        users = club.applicants()
        return redirect('applicant_list', club_id=club.id)


class MemberListView(LoginRequiredMixin, ApplicantProhibitedMixin, ListView, MultipleObjectMixin):
    """View that shows a list of all the members."""

    model = User
    template_name = "member_list.html"
    context_object_name = "users"
    paginate_by = settings.NUMBER_PER_PAGE

    def get_queryset(self):
        club = Club.objects.get(id=self.kwargs['club_id'])
        users = club.members()
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
        users = club.members()
        return redirect('member_list', club_id=club.id)


class OwnerListView(LoginRequiredMixin, ListView, MultipleObjectMixin):
    """View that shows a list of all the owners."""

    model = User
    template_name = "owner_list.html"
    context_object_name = "users"
    paginate_by = settings.NUMBER_PER_PAGE

    def get_queryset(self):
        club = Club.objects.get(id=self.kwargs['club_id'])
        users = club.owners()
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
