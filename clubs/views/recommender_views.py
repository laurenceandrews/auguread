"""Views related to the recommender."""
from clubs.forms import ClubRecommenderForm
# from clubs.helpers import member, owner
from clubs.models import Club, User, Club_Users
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.db.models import Q

@login_required
def RecommendationsView(request):
    """View that shows a list of all recommended books."""
    return render(request, 'rec_page.html')

class ClubRecommenderView(LoginRequiredMixin, View):
    """View that handles the club recommendations."""
    model = Club_Users
    template_name = 'club_recommender.html'
    form_class = ClubRecommenderForm
    # http_method_names = ['get', 'post']

    def get(self, request):
        """Display template."""

        self.clubs_queryset = Club.objects.all().order_by('name')
        query = request.GET.get('q')
        if query:
            self.clubs_queryset = Club.objects.filter(
                Q(name__icontains=query) | Q(location__icontains=query)
            ).distinct()

        paginator = Paginator(self.clubs_queryset, settings.CLUBS_PER_PAGE)
        page_number = request.GET.get('page')
        self.clubs_paginated = paginator.get_page(page_number)

        self.next = request.GET.get('next') or ''
        return self.render()

    def get_form_kwargs(self):
        kwargs = super(ClubRecommenderView, self).get_form_kwargs()
        kwargs['id'] = self.kwargs['id']
        return kwargs

    # def form_valid(self, form):
    #     user = User.objects.get(id = self.kwargs['id'])
    #     club = form.cleaned_data.get('club')
    #     return render(self.request, 'club_recommender.html')
    
    def get_data(self, **kwargs):
        data = super().get_data(**kwargs)
        user = User.objects.get(id = self.kwargs['id'])
        data['first_name'] = user.first_name

    def render(self):
        """Render template with blank form."""

        return render(self.request, 'club_recommender.html', {'next': self.next, 'clubs_paginated': self.clubs_paginated})

