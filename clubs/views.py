from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth import login, logout
from clubs.forms import LogInForm, PasswordForm, NewClubForm
from django.views import View
from .forms import SignUpForm
from .helpers import login_prohibited
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView, UpdateView, CreateView
from django.urls import reverse
from django.http import Http404
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.list import MultipleObjectMixin
from clubs.models import Post, User, Club
from django.contrib.auth.decorators import login_required
from clubs.helpers import member, owner


class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        """Returns the url to redirect to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        else:
            return self.redirect_when_logged_in_url

class LogInView(LoginProhibitedMixin, View):
    """View that handles log in."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = 'rec'

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
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})


def home(request):
    return render(request, 'home.html')

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

class ShowUserView(LoginRequiredMixin, DetailView, MultipleObjectMixin):
    """View that shows individual user details."""

    model = User
    template_name = 'show_user.html'
    paginate_by = settings.POSTS_PER_PAGE
    pk_url_kwarg = 'user_id'

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""
        user = self.get_object()
        posts = Post.objects.filter(author=user)
        context = super().get_context_data(object_list=posts, **kwargs)
        context['user'] = user
        context['posts'] = context['object_list']
        context['following'] = self.request.user.is_following(user)
        context['followable'] = (self.request.user != user)
        return context

    def get(self, request, *args, **kwargs):
        """Handle get request, and redirect to user_list if user_id invalid."""

        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect('user_list')

class UserListView(LoginRequiredMixin, ListView):
    """View that shows a list of all users."""

    model = User
    template_name = "user_list.html"
    context_object_name = "users"
    paginate_by = settings.USERS_PER_PAGE


"""Add LoginRequiredMixin to rec-view once log in redirect is fixed"""
def RecommendationsView(request):
    """View that shows a list of all recommended books."""
    return render(request, 'rec_page.html')

class NewClubView(LoginRequiredMixin, CreateView):
    """Class-based generic view for new club handling."""

    model = Club
    template_name = 'new_club.html'
    form_class = NewClubForm
    http_method_names = ['post', 'get']

    def form_valid(self, form):
        """Process a valid form."""
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        return reverse('club_list')

    def handle_no_permission(self):
        return redirect('log_in')

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
        return redirect('club_list', club_id=club_id)
    else:
        return redirect('show_user', user_id=user_id, club_id=club_id)
