from clubs.models import Club, Club_Users, Book_Rating
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from schedule.models import Calendar, Event, Rule


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
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)


class MemberProhibitedMixin:
    """Redirects to club_list if user is an applicant or a member and dispatches as normal otherwise."""

    def dispatch(self, *args, **kwargs):
        """Checks the membership type of the user of the club with the given club id."""

        club = Club.objects.get(id=kwargs['club_id'])
        if self.request.user in club.owners.all() or club.owner == self.request.user:
            return super().dispatch(*args, **kwargs)
        else:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)


class ClubOwnerRequiredMixin:
    """Mixin that redirects when a user is not the club owner."""

    redirect_when_not_a_club_owner_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def dispatch(self, *args, **kwargs):
        """Redirect when not a club_user, or dispatch as normal otherwise."""
        calendar_slug = kwargs['calendar_slug']
        calendar = Calendar.objects.get(slug=calendar_slug)
        club = Club.objects.get(calendar=calendar)
        if self.request.user == club.owner:
            return super().dispatch(*args, **kwargs)
        return self.handle_not_a_club_owner(*args, **kwargs)

    def handle_not_a_club_owner(self, *args, **kwargs):
        calendar_slug = kwargs['calendar_slug']
        calendar = Calendar.objects.get(slug=calendar_slug)
        url = reverse('full_calendar', kwargs={'calendar_slug': calendar.slug})
        messages.add_message(self.request, messages.ERROR, "Only the club owner can perform this action!")
        return redirect(url)


class ClubUserRequiredMixin:
    """Mixin that redirects when a user does not have a Club_Users relationship."""

    redirect_when_not_a_club_user_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def dispatch(self, *args, **kwargs):
        """Redirect when not a club_user, or dispatch as normal otherwise."""
        calendar_slug = kwargs['calendar_slug']
        calendar = Calendar.objects.get(slug=calendar_slug)
        club = Club.objects.get(calendar=calendar)
        club_user_relationship_exists = Club_Users.objects.filter(club=club, user=self.request.user)
        if not club_user_relationship_exists:
            return self.handle_not_a_club_user(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_not_a_club_user(self, *args, **kwargs):
        calendar_slug = kwargs['calendar_slug']
        calendar = Calendar.objects.get(slug=calendar_slug)
        url = reverse('full_calendar', kwargs={'calendar_slug': calendar.slug})
        messages.add_message(self.request, messages.ERROR, "You are not a user of this club!")
        return redirect(url)

class TenPosRatingsRequiredMixin:
    """Mixin that redirects when a user has not yet made ten positive book ratings."""

    redirect_when_less_than_ten_pos_ratings_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def dispatch(self, *args, **kwargs):
        """Redirect when ten pos ratings not met, or dispatch as normal otherwise."""
        if self.has_less_than_ten_pos_ratings():
            return self.handle_less_than_ten_pos_ratings(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def has_less_than_ten_pos_ratings(self, *args, **kwargs):
        less_than_ten_pos_ratings = True

        user = self.request.user
        POSITIVE_RATINGS = [6, 7, 8, 9, 10]
        
        positive_book_rating_count = Book_Rating.objects.filter(user = user, rating__in=POSITIVE_RATINGS).count()
        if positive_book_rating_count >= 10:
            less_than_ten_pos_ratings = False

        return less_than_ten_pos_ratings

    def handle_less_than_ten_pos_ratings(self, *args, **kwargs):
        url = self.redirect_when_less_than_ten_pos_ratings_url
        return redirect(url)