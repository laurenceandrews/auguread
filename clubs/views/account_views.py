"""Views related to the account."""
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from clubs.forms import PasswordForm, UserForm, SignUpForm, LogInForm
from .mixins import LoginProhibitedMixin
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.views import View
from clubs.helpers import login_prohibited


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
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        user = form.get_user()
        if user is not None:
            login(request, user)
            redirect_url = request.POST.get(
                'next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
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
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)
