from clubs.forms import LogInForm, PasswordForm, SignUpForm
from clubs.models import Club, Post, User
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
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


class LogInView(LoginProhibitedMixin, View):
    """View that handles log in."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = 'book_preferences'

    def get(self, request):
        """Display log in template."""
        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handles log in attempt."""

        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.AUTO_REDIRECT_URL
        user = form.get_user()
        if user is not None:
            login(request, user)
            redirect_url = request.POST.get(
                'next') or settings.AUTO_REDIRECT_URL
            return redirect(redirect_url)
        messages.add_message(request, messages.ERROR,
                             "The credentials provided are invalid!")
        return self.render()

    def render(self):
        """Render log in template with blank log in form."""

        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})


def log_out(request):
    logout(request)
    return redirect('home')


@login_prohibited
def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('book_preferences')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})


class PasswordView(LoginRequiredMixin, FormView):
    """View that handles password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""

        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""

        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""

        messages.add_message(
            self.request, messages.SUCCESS, "Password updated!")
        return reverse(settings.AUTO_REDIRECT_URL)


class UserListView(LoginRequiredMixin, ListView, MultipleObjectMixin, ApplicantProhibitedMixin):
    """View that shows a list of all users"""
    model = User
    template_name = "user_list.html"
    context_object_name = "users"
    paginate_by = settings.NUMBER_PER_PAGE

    def get_queryset(self):
        club = Club.objects.get(id=self.kwargs['club_id'])
        users = list(club.members.all()) + list(club.owners.all()) + [club.owner]
        return users

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        club = Club.objects.get(id=self.kwargs['club_id'])
        context['club'] = club
        context['user'] = self.request.user

        return context


class ShowUserView(LoginRequiredMixin, DetailView, MultipleObjectMixin, ApplicantProhibitedMixin):
    """View that shows individual user details."""

    model = User
    template_name = 'show_user.html'
    paginate_by = settings.NUMBER_PER_PAGE
    pk_url_kwarg = 'user_id'

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""
        club = Club.objects.get(id=self.kwargs['club_id'])
        target = self.get_object()
        user = self.request.user
        users = User.objects.all()
        target_type = target.membership_type(club)
        is_owner = target_type == 'Owner'
        user_type = user.membership_type(club)
        posts = Post.objects.filter(author=user)
        context = super().get_context_data(object_list=users, **kwargs)
        context['can_approve'] = ((user != target) and (user_type == 'Owner'
                                                        or user == club.owner) and target_type == 'Applicant')
        context['is_owner'] = target_type == 'Owner'
        context['can_transfer'] = ((user != target) and user == club.owner
                                   and is_owner)
        context['type'] = target_type
        context['user'] = user
        context['posts'] = context['object_list']
        context['following'] = self.request.user.is_following(user)
        context['followable'] = (self.request.user != user)
        context['target'] = target
        context['club'] = club
        return context

    def get(self, request, *args, **kwargs):
        """Handle get request, and redirect to user_list if user_id invalid."""
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect('user_list', club_id=self.kwargs['club_id'])


@login_required
def user_detail(request):
    user = request.user
    return render(request, 'user_detail.html', {'target': user})
