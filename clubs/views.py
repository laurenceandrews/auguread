from clubs.forms import (AddressForm, LogInForm, NewClubForm, PasswordForm,
                         PostForm, SignUpForm)
from clubs.helpers import member, owner
from clubs.models import (Address, Book, Club, MeetingAddress, MeetingLink,
                          Post, User)
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
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

from .forms import (CalendarPickerForm, CreateEventForm, MeetingAddressForm,
                    MeetingLinkForm, SignUpForm)
from .helpers import login_prohibited


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


@login_required
def club_list(request):
    clubs = Club.objects.all()
    paginator = Paginator(clubs, settings.NUMBER_PER_PAGE)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        'club_list.html',
        {
            "page_obj": page_obj,
            "clubs": clubs,
        }
    )


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


def calendar_picker(request):
    if request.method == 'POST':
        form = CalendarPickerForm(request.POST)
        if form.is_valid():
            calendar = form.cleaned_data.get('calendar')
            return render(request, 'fullcalendar.html', {'calendar': calendar})
    else:
        form = CalendarPickerForm()
    return render(request, 'calendar_picker.html', {'form': form})


def full_calendar(request, calendar_slug):
    calendar = Calendar.objects.get(slug=calendar_slug)
    return render(request, 'fullcalendar.html', {'calendar': calendar})


def events_list(request, calendar_id):
    calendar = Calendar.objects.get(id=calendar_id)
    events = calendar.event_set.all()
    return render(request, "events_list.html",
                  {
                      'calendar': calendar,
                      'events': events,
                  })


class CreateEventView(CreateView):
    model = Event
    template_name = 'event_create.html'
    form_class = CreateEventForm

    def form_valid(self, form):
        """Process a valid form."""
        calendar = Calendar.objects.get(id=self.kwargs['calendar_id'])

        title = form.cleaned_data.get('title')
        start = form.cleaned_data.get('start')
        end = form.cleaned_data.get('end')
        end_recurring_period = form.cleaned_data.get('end_recurring_period')
        rule = form.cleaned_data.get('rule')

        event = Event.objects.create(
            title=title,
            start=start,
            end=end,
            end_recurring_period=end_recurring_period,
            rule=rule,
            calendar=calendar
        )

        club = Club.objects.get(calendar=event.calendar)

        if club.meeting_type == 'ONL':
            return redirect('create_event_link', calendar_slug=calendar.slug, event_id=event.id)

        if club.meeting_type == 'INP':
            return redirect('create_event_address', calendar_slug=calendar.slug, event_id=event.id)

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        calendar = Calendar.objects.get(id=self.kwargs['calendar_id'])
        return reverse('full_calendar', kwargs={'calendar_slug': calendar.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar = Calendar.objects.get(id=self.kwargs['calendar_id'])
        context['calendar'] = calendar
        context['calendar_id'] = calendar.id
        context['calendar_name'] = calendar.name
        context['user'] = self.request.user

        return context


class CreateEventLinkView(CreateView):
    model = MeetingLink
    template_name = 'event_link_form.html'
    form_class = MeetingLinkForm

    def form_valid(self, form):
        """Process a valid form."""
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        event = Event.objects.get(id=self.kwargs['event_id'])

        meeting_link = form.cleaned_data.get('meeting_link')

        meeting_link_object = MeetingLink.objects.create(
            event=event,
            meeting_link=meeting_link
        )
        return render(self.request, 'fullcalendar.html', {'calendar': event.calendar})

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        return reverse('full_calendar', kwargs={'calendar_slug': calendar.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = Event.objects.get(id=self.kwargs['event_id'])
        context['event'] = event

        return context


class CreateEventAddressView(CreateView):
    model = MeetingAddress
    template_name = 'event_address_create.html'
    form_class = MeetingAddressForm

    def form_valid(self, form):
        """Process a valid form."""
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        event = Event.objects.get(id=self.kwargs['event_id'])

        address = form.cleaned_data.get('address')

        meeting_address_object = MeetingAddress.objects.create(
            event=event,
            address=address
        )
        return render(self.request, 'fullcalendar.html', {'calendar': event.calendar})

    def get_form_kwargs(self):
        kwargs = super(CreateEventAddressView, self).get_form_kwargs()
        kwargs['calendar_slug'] = self.kwargs['calendar_slug']
        return kwargs

    def get_create_address_url(self):
        """Return URl to redirect the user to if selected to create a new address"""
        return reverse('create_address', kwargs={'calendar_slug': self.kwargs['calendar_slug'], 'event_id': self.kwargs['event_id']})

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        return reverse('full_calendar', kwargs={'calendar_slug': calendar.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = Event.objects.get(id=self.kwargs['event_id'])
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        context['calendar'] = calendar
        context['calendar_id'] = calendar.id
        context['event'] = event

        return context


class CreateAddressView(CreateView):
    model = Address
    template_name = 'address_create.html'
    form_class = AddressForm

    def form_valid(self, form):
        """Process a valid form."""
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        event = Event.objects.get(id=self.kwargs['event_id'])

        name = form.cleaned_data.get('name')
        address1 = form.cleaned_data.get('address1')
        address2 = form.cleaned_data.get('address2')
        zip_code = form.cleaned_data.get('zip_code')
        city = form.cleaned_data.get('city')
        country = form.cleaned_data.get('country')

        address = Address.objects.create(
            name=name,
            address1=address1,
            address2=address2,
            zip_code=zip_code,
            city=city,
            country=country
        )

        event_exists = MeetingAddress.objects.filter(event=event).exists()

        if event_exists:
            meeting_address_object = MeetingAddress.objects.get(
                event=event
            )
            meeting_address_object.address = address
            meeting_address_object.save()
        else:
            meeting_address_object = MeetingAddress.objects.create(
                event=event,
                address=address
            )

        return redirect('full_calendar', calendar_slug=calendar.slug)

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        return reverse('full_calendar', kwargs={'calendar_slug': self.kwargs['calendar_slug']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        context['calendar'] = calendar
        context['calendar_id'] = calendar.id
        event = Event.objects.get(id=self.kwargs['event_id'])
        context['event'] = event

        return context


class EditEventView(UpdateView):
    model = Event
    template_name = 'event_update.html'
    form_class = CreateEventForm
    pk_url_kwarg = "event_id"

    def form_valid(self, form):
        event = form.save()

        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        club = Club.objects.get(calendar=event.calendar)

        if club.meeting_type == 'ONL':
            return redirect('edit_event_link', calendar_slug=calendar.slug, event_id=event.id)

        if club.meeting_type == 'INP':
            return redirect('edit_event_address', calendar_slug=calendar.slug, event_id=event.id)

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        return reverse('full_calendar', kwargs={'calendar_slug': self.kwargs['calendar_slug']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        context['calendar'] = calendar
        context['calendar_id'] = calendar.id
        context['calendar_name'] = calendar.name
        context['user'] = self.request.user

        return context


class EditEventLinkView(UpdateView):
    model = Event
    template_name = 'event_link_update.html'
    form_class = MeetingLinkForm
    pk_url_kwarg = "event_id"

    def form_valid(self, form):
        """Process a valid form."""
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        event = Event.objects.get(id=self.kwargs['event_id'])

        meeting_link = form.cleaned_data.get('meeting_link')

        meeting_link_object = MeetingLink.objects.get(event=event)

        meeting_link_object.meeting_link = meeting_link

        meeting_link_object.save()
        return render(self.request, 'fullcalendar.html', {'calendar': event.calendar})

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        return reverse('full_calendar', kwargs={'calendar_slug': self.kwargs['calendar_slug']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        event = Event.objects.get(id=self.kwargs['event_id'])
        context['calendar'] = calendar
        context['calendar_id'] = calendar.id
        context['calendar_name'] = calendar.name
        context['event_name'] = event.title
        context['user'] = self.request.user

        return context


class EditEventAddressView(UpdateView):
    model = Event
    template_name = 'event_address_update.html'
    form_class = MeetingAddressForm
    pk_url_kwarg = "event_id"

    def get_form_kwargs(self):
        kwargs = super(EditEventAddressView, self).get_form_kwargs()
        kwargs['calendar_slug'] = self.kwargs['calendar_slug']
        return kwargs

    def form_valid(self, form):
        """Process a valid form."""
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        event = Event.objects.get(id=self.kwargs['event_id'])

        address = form.cleaned_data.get('address')

        meeting_address_object = MeetingAddress.objects.get(event=event)

        meeting_address_object.address = address

        meeting_address_object.save()
        return render(self.request, 'fullcalendar.html', {'calendar': event.calendar})

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        return reverse('full_calendar', kwargs={'calendar_slug': self.kwargs['calendar_slug']})

    def get_create_address_url(self):
        """Return URl to redirect the user to if selected to create a new address"""
        return reverse('create_address', kwargs={'calendar_slug': self.kwargs['calendar_slug'], 'event_id': self.kwargs['event_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        event = Event.objects.get(id=self.kwargs['event_id'])
        context['calendar'] = calendar
        context['calendar_id'] = calendar.id
        context['calendar_slug'] = calendar.slug
        context['calendar_name'] = calendar.name
        context['event_name'] = event.title
        context['user'] = self.request.user

        return context


class DeleteEventView(DeleteView):
    model = Event
    template_name = 'event_delete.html'
    form_class = CreateEventForm
    pk_url_kwarg = "event_id"

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        return reverse('full_calendar', kwargs={'calendar_slug': calendar.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar = Calendar.objects.get(slug=self.kwargs['calendar_slug'])
        context['calendar'] = calendar
        context['calendar_id'] = calendar.id
        context['calendar_name'] = calendar.name
        context['user'] = self.request.user

        return context


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
