"""Views related to all types of users"""
from clubs.forms import LogInForm, PasswordForm, SignUpForm, UserDeleteForm
from clubs.models import Club, User
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView
from django.views.generic.detail import DetailView
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

class UserDetailList(LoginRequiredMixin, ListView):
    """View that shows a list of all users."""

    model = User
    template_name = "user_detail_list.html"
    context_object_name = "users"
    paginate_by = settings.USERS_PER_PAGE

class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    template_name = 'user_detail.html'
    pk_url_kwarg = "user_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        current_user = self.request.user
        context['current_user'] = current_user
        context['current_user_is_following_user'] = current_user.is_following(user)

        clubs = user.clubs_attended()
        context['clubs'] = clubs

        paginator = Paginator(clubs, settings.NUMBER_PER_PAGE)

        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj

        return context

    def get(self, request, *args, **kwargs):
        """Handle get request, and redirect if user_id invalid."""

        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            messages.add_message(self.request, messages.ERROR, "Invalid user!")
            return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))


@login_required
def user_profile_view(request):
    user = request.user
    clubs = user.clubs_attended()

    paginator = Paginator(clubs, settings.NUMBER_PER_PAGE)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'user_detail.html',
                  {'target': user,
                   'user_profile': True,
                   'clubs': clubs,
                   'page_obj': page_obj
                   })


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
