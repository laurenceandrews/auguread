from clubs.forms import (AddressForm, CalendarPickerForm, CreateEventForm,
                         LogInForm, MeetingAddressForm, MeetingLinkForm,
                         NewClubForm, PasswordForm, PostForm, SignUpForm)
from clubs.models import (Address, Book, BookRatingForm, Club, MeetingAddress,
                          MeetingLink, Post, User)
from clubs.views.helpers import member, owner
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.http import (Http404, HttpResponse, HttpResponseForbidden,
                         HttpResponseRedirect)
from django.shortcuts import redirect, render
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.views import View
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)
from django.views.generic.list import MultipleObjectMixin
from schedule.models import Calendar, Event, Rule

from .helpers import login_prohibited
from .mixins import LoginProhibitedMixin


class ApplicantProhibitedMixin:
    """Redirects to club_list if user is an applicant and dispatches as normal otherwise."""

    def dispatch(self, *args, **kwargs):
        """Checks the membership type of the user of the club."""

        club = Club.objects.get(id=kwargs['club_id'])
        if (self.request.user in club.members.all()
                or self.request.user in club.owners.all() or club.owner == self.request.user):
            return super().dispatch(*args, **kwargs)
        else:
            return redirect(settings.AUTO_REDIRECT_URL)


class MemberProhibitedMixin:
    """Redirects to club_list if user is an applicant or a member and dispatches as normal otherwise."""

    def dispatch(self, *args, **kwargs):
        """Checks the membership type of the user of the club with the given club id."""

        club = Club.objects.get(id=kwargs['club_id'])
        if self.request.user in club.owners.all() or club.owner == self.request.user:
            return super().dispatch(*args, **kwargs)
        else:
            return redirect(settings.AUTO_REDIRECT_URL)


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


class FeedView(LoginRequiredMixin, ListView):
    """Class-based generic view for displaying a view."""

    model = Post
    template_name = "feed.html"
    context_object_name = 'posts'
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        """Return the user's feed."""
        current_user = self.request.user
        authors = list(current_user.followees.all()) + [current_user]
        posts = Post.objects.filter(author__in=authors)
        return posts

    def get_context_data(self, **kwargs):
        """Return context data, including new post form."""
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['form'] = PostForm()
        return context


@login_required
def follow_toggle(request, user_id):
    current_user = request.user
    try:
        followee = User.objects.get(id=user_id)
        current_user.toggle_follow(followee)
    except ObjectDoesNotExist:
        return redirect('user_list')
    else:
        return redirect('show_user', user_id=user_id)


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


@login_required
def RecommendationsView(request):
    """View that shows a list of all recommended books."""
    return render(request, 'rec_page.html')


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


# @login_required
# def club_list(request):
#     clubs = Club.objects.all()
#     paginator = Paginator(clubs, settings.NUMBER_PER_PAGE)
#
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     return render(
#         request,
#         'club_list.html',
#         {
#             "page_obj": page_obj,
#             "clubs": clubs,
#         }
#     )

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


class NewPostView(LoginRequiredMixin, CreateView):
    """Class-based generic view for new post handling."""

    model = Post
    template_name = 'feed.html'
    form_class = PostForm
    http_method_names = ['post']

    def form_valid(self, form):
        """Process a valid form."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        return reverse('feed')

    def handle_no_permission(self):
        return redirect('log_in')


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


def book_preferences(request):
    """View that allows the user to view all books and rate them."""
    books_queryset = Book.objects.all()

    paginator = Paginator(books_queryset, settings.BOOKS_PER_PAGE)
    page_number = request.GET.get('page')
    books_paginated = paginator.get_page(page_number)

    return render(request, 'book_preferences.html', {'current_user': request.user, 'books_queryset': books_queryset, 'books_paginated': books_paginated})


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


class BookPreferencesView(LoginRequiredMixin, View):
    """View that handles book preferences."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = 'book_preferences'

    books_queryset = Book.objects.all()
    paginator = Paginator(books_queryset, settings.BOOKS_PER_PAGE)

    def get(self, request):
        """Display log in template."""

        page_number = request.GET.get('page')
        books_paginated = self.paginator.get_page(page_number)

        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handles submit attempt."""

        form = BookRatingForm(request.POST)
        self.next = request.POST.get('next') or settings.AUTO_REDIRECT_URL

        return self.render()

    def render(self):
        """Render template with blank form."""

        form = BookRatingForm()
        return render(self.request, 'book_preferences.html', {'form': form, 'next': self.next})
