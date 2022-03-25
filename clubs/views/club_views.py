"""Views related to the clubs."""
from clubs.forms import (BookRatingForm, ClubUpdateForm, CreateClubUserForm,
                         NewClubForm)
from clubs.models import Club, Club_Users, Post, User
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, UpdateView
from django.views.generic.list import MultipleObjectMixin
from schedule.models import Calendar, Event, Rule

from .helpers import login_prohibited, member, owner
from .mixins import (ApplicantProhibitedMixin, LoginProhibitedMixin,
                     MemberProhibitedMixin)

"""View that handles creating a new club."""


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

            Club_Users.objects.create(user=current_user, club=club, role_num=4)
            return redirect('club_detail', club.id)
        else:
            return render(request, "new_club.html", {"form": form})
    else:
        return render(request, "new_club.html", {"form": NewClubForm})


class ClubUpdateView(LoginRequiredMixin, UpdateView):
    """ View that handles club edit requests. """

    model = Club
    template_name = 'club_update_view.html'
    form_class = ClubUpdateForm
    pk_url_kwarg = "club_id"

    # def get_form_kwargs(self):
    #     kwargs = super(ClubUpdateView, self).get_form_kwargs()
    #     kwargs['club_id'] = self.kwargs['club_id']
    #     return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""
        club = Club.objects.get(id=self.kwargs['club_id'])

        name = form.cleaned_data.get("name")
        # city = form.cleaned_data.get("city")
        # country = form.cleaned_data.get("country")
        description = form.cleaned_data.get("description")

        # location = city + ", " + country

        meeting_type = form.cleaned_data.get("meeting_type")

        club.name = name
        # club.location = location
        club.description = description
        club.meeting_type = meeting_type
        club.save()

        return redirect('club_detail', club_id=club.id)

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        club = Club.objects.get(id=self.kwargs['club_id'])
        return reverse('club_detail', kwargs={'club_id': club.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        club = Club.objects.get(id=self.kwargs['club_id'])
        context['club'] = club

        return context


class DeleteClubView(LoginRequiredMixin, DeleteView):
    """ View that handles club delete requests. """

    model = Club
    template_name = 'club_delete.html'
    form_class = NewClubForm
    pk_url_kwarg = "club_id"

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        return reverse('user_clubs', kwargs={'role_num': '4'})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        club = Club.objects.get(id=self.kwargs['club_id'])
        context['club'] = club

        return context


class DeleteClubUserView(LoginRequiredMixin, DeleteView):
    """ View that handles club user delete requests. """

    model = Club_Users
    template_name = 'club_user_delete.html'
    form_class = CreateClubUserForm
    pk_url_kwarg = "club_users_id"

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        club_user = Club_Users.objects.get(id=self.kwargs['club_users_id'])
        club = club_user.club.name
        messages.add_message(self.request, messages.SUCCESS, "Success!")
        return reverse('club_detail', kwargs={'club_id': club_user.club.id})

    def get_cancel_url(self):
        """Return URL to redirect the user too after form handling cancelled."""
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        club_user = Club_Users.objects.get(id=self.kwargs['club_users_id'])
        confirmation_text = "Invalid request"
        if club_user.role_num == '1':
            confirmation_text = f'You will be deleting the application for {club_user.user.full_name()} in {club_user.club.name}.'
        if club_user.role_num == '2':
            confirmation_text = f'You will be deleting the membership for {club_user.user.full_name()} in {club_user.club.name}.'
        if club_user.role_num == '4':
            confirmation_text = f'You will be deleting the ownership for {club_user.user.full_name()} in {club_user.club.name}.'
        context['membership_type'] = club_user.get_role_num_display
        context['confirmation_text'] = confirmation_text
        return context


class ClubDetailView(LoginRequiredMixin, DetailView):

    model = Club
    template_name = 'club_detail.html'
    pk_url_kwarg = "club_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        context['form'] = BookRatingForm()

        return context

    def get(self, request, *args, **kwargs):
        """Handle get request, and redirect to user_list if book_id invalid."""

        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            messages.add_message(self.request, messages.ERROR, "Invalid book!")
            return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))


class ClubListView(LoginRequiredMixin, ListView):
    """View to display a list of available clubs."""

    paginate_by = settings.NUMBER_PER_PAGE
    model = Club
    template_name = "club_list.html"
    context_object_name = "clubs"

    def get_queryset(self):

        clubs = Club.objects.all()

        query = self.request.GET.get('q')
        if query:
            clubs = clubs.filter(
                Q(name__icontains=query) | Q(location__icontains=query)
            ).distinct()
        return clubs


@ login_required
@ member
def enter(request, club_id):
    """View that handles entering a club."""
    user = request.user
    return redirect('show_user', user_id=user.id, club_id=club_id)


@ login_required
def apply(request, club_id):
    """View that handles applying for a club."""
    user = request.user
    club = Club.objects.get(id=club_id)
    club.applied_by(user)
    messages.add_message(request, messages.SUCCESS, "Application created!")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@ login_required
@ owner
def approve(request, user_id, club_id):
    """View that handles approving applicants for a club."""

    club = Club.objects.get(id=club_id)
    try:
        user = User.objects.get(id=user_id)
        club.accept(user)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "Invalid applicant!")
        return redirect('applicant_list', club_id=club_id)
    else:
        messages.add_message(request, messages.SUCCESS, "Application approved!")
        return redirect('applicant_list', club_id=club_id)


@ login_required
@ owner
def transfer(request, user_id, club_id):
    """View that handles transfering ownership of a club."""

    club = Club.objects.get(id=club_id)
    target = User.objects.get(id=user_id)
    club.transfer(target)
    try:
        target = User.objects.get(id=user_id)
        club.transfer(target)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "Invalid member!")
        return redirect('member_list', club_id=club_id)
    else:
        messages.add_message(request, messages.SUCCESS, "Club ownership transfered approved!")
        return redirect('member_list', club_id=club_id)


class ShowUserView(LoginRequiredMixin, ApplicantProhibitedMixin, DetailView, MultipleObjectMixin):
    """View that shows individual user details."""

    model = User
    template_name = 'show_user.html'
    paginate_by = settings.NUMBER_PER_PAGE
    pk_url_kwarg = 'user_id'

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""
        # user = self.get_object() #new
        club = Club.objects.get(id=self.kwargs['club_id'])
        target = self.get_object()
        user = self.request.user
        users = User.objects.all()
        target_type = target.membership_type(club)
        is_owner = target_type == 'Owner'
        user_type = user.membership_type(club)
        posts = Post.objects.filter(author=user)
        context = super().get_context_data(object_list=users, **kwargs)
        context = super().get_context_data(object_list=posts, **kwargs)  # new
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


@ login_required
@ owner
def applicants_list(request, club_id):
    """ View to display a club's applicants list. """
    club = Club.objects.get(id=club_id)
    applicants = club.applicants()
    paginator = Paginator(applicants, settings.NUMBER_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "club_users_list.html",
                  {
                      'list_of_applicants': True,
                      'club': club,
                      'user': request.user,
                      'users': applicants,
                      'page_obj': page_obj
                  })


@ login_required
@ member
def members_list(request, club_id):
    """ View to display a club's applicants list. """
    club = Club.objects.get(id=club_id)
    members = club.members()
    paginator = Paginator(members, settings.NUMBER_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "club_users_list.html",
                  {
                      'list_of_members': True,
                      'club': club,
                      'is_owner': request.user.is_owner(club),
                      'user': request.user,
                      'users': members,
                      'page_obj': page_obj
                  })


class OwnerListView(LoginRequiredMixin, ListView, MultipleObjectMixin):
    """View that shows a list of all the owners."""

    model = User
    template_name = "owner_list.html"
    context_object_name = "users"
    paginate_by = settings.NUMBER_PER_PAGE

    def get_queryset(self):
        club = Club.objects.get(id=self.kwargs['club_id'])
        users = list(club.owners())
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
