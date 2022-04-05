"""Views related to all types of users"""
from clubs.forms import LogInForm, PasswordForm, SignUpForm, UserDeleteForm
from clubs.models import Club, User
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from clubs.views.mixins import PosRatingsRequiredMixin
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
from .mixins import LoginProhibitedMixin


class UserDetailList(LoginRequiredMixin, ListView):
    """View that shows a list of all users."""

    model = User
    template_name = "user_detail_list.html"
    context_object_name = "users"
    paginate_by = settings.USERS_PER_PAGE


class UserDetailView(LoginRequiredMixin, PosRatingsRequiredMixin, DetailView):

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

        friends = user.friends_list
        context['friends'] = friends

        paginator = Paginator(clubs, settings.NUMBER_PER_PAGE)

        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj

        return context

    def get(self, request, *args, **kwargs):
        """Handle get request, and redirect if user_id invalid."""

        try:
            user = self.get_object()
            current_user = self.request.user
            if current_user == user:
                return redirect('user_profile')

            return super().get(request, *args, **kwargs)
        except Http404:
            messages.add_message(self.request, messages.ERROR, "Invalid user!")
            return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))


@login_required
def user_profile_view(request):
    user = request.user
    clubs = user.clubs_attended()

    friends = user.friends_list

    paginator = Paginator(clubs, settings.NUMBER_PER_PAGE)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'user_detail.html',
                  {'target': user,
                   'user_profile': True,
                   'clubs': clubs,
                   'friends': friends,
                   'page_obj': page_obj
                   })
