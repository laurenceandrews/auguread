"""Views for the mixins."""
from django.shortcuts import redirect
from clubs.models import Club
from django.conf import settings

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
