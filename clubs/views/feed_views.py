"""Views related to the Feed."""
from clubs.forms import PostForm
from clubs.models import Club, ClubFeedPost, Post, User
from clubs.views.mixins import ClubMemberOrOwnerRequiredMixin
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.edit import CreateView


class ClubFeedPostCreateView(LoginRequiredMixin, ClubMemberOrOwnerRequiredMixin, CreateView):
    model = Post
    template_name = 'club_feed.html'
    form_class = PostForm

    def form_valid(self, form):
        """Process a valid form."""

        club = Club.objects.get(id=self.kwargs['club_id'])

        text = form.cleaned_data.get('text')
        author = self.request.user

        post = Post.objects.create(author=author, text=text)

        club_feed_post = ClubFeedPost.objects.create(club=club, post=post)

        messages.add_message(self.request, messages.SUCCESS, "Post created!")

        return redirect('club_feed', club.id)


class ClubFeedView(LoginRequiredMixin, ClubMemberOrOwnerRequiredMixin, ListView):
    """Class-based generic view for displaying a club's feed."""

    model = Post
    template_name = "club_feed.html"
    context_object_name = 'posts'
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        """Return the club's feed."""
        current_user = self.request.user
        club = Club.objects.get(id=self.kwargs['club_id'])
        club_feed_posts_ids = ClubFeedPost.objects.filter(club=club).values_list('post', flat=True)
        posts = Post.objects.filter(id__in=club_feed_posts_ids)
        return posts

    def get_context_data(self, **kwargs):
        """Return context data, including new post form."""
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['form'] = PostForm()
        club = Club.objects.get(id=self.kwargs['club_id'])
        context['club'] = club
        return context
