"""Views related to the Feed."""
from clubs.forms import PostForm
from clubs.models import Club, ClubFeed, Post, User
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


class FeedView(LoginRequiredMixin, ListView):
    """Class-based generic view for displaying the feed."""

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


class ClubFeedPostCreateView(CreateView):
    model = Post
    # fields = ['post']
    template_name = 'feed.html'
    form_class = PostForm

    def form_valid(self, form):
        """Process a valid form."""

        club = Club.objects.get(id=self.kwargs['club_id'])

        text = form.cleaned_data.get('text')
        author = self.request.user

        post = Post.objects.create(author=author, text=text)

        club_feed = ClubFeed.objects.get(club=club)
        club_feed.posts.add(post)

        messages.add_message(self.request, messages.SUCCESS, "Post created!")

        return redirect('feed')
