"""Views related to the Feed."""
from clubs.forms import PostForm
from clubs.models import Club, ClubFeedPost, Post, PostComment, User
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


class PostCommentsView(LoginRequiredMixin, ClubMemberOrOwnerRequiredMixin, ListView):
    """Class-based generic view for displaying a club's feed."""

    model = Post
    template_name = "post_comments.html"
    context_object_name = 'comments'
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        """Return the club's feed."""
        current_user = self.request.user
        post = Post.objects.get(id=self.kwargs['post_id'])
        comment_ids = PostComment.objects.filter(post=post).values_list('comment', flat=True)
        comments = Post.objects.filter(id__in=comment_ids)
        return comments

    def get_context_data(self, **kwargs):
        """Return context data, including new post form."""
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['form'] = PostForm()
        club = Club.objects.get(id=self.kwargs['club_id'])
        context['club'] = club
        post = Post.objects.get(id=self.kwargs['post_id'])
        context['post'] = post
        context['original_post'] = [post]
        return context


class PostCommentsCreateView(LoginRequiredMixin, ClubMemberOrOwnerRequiredMixin, CreateView):
    model = PostComment
    template_name = 'post_comments.html'
    form_class = PostForm

    def form_valid(self, form):
        """Process a valid form."""

        club = Club.objects.get(id=self.kwargs['club_id'])
        post = Post.objects.get(id=self.kwargs['post_id'])

        text = form.cleaned_data.get('text')
        author = self.request.user

        comment = Post.objects.create(author=author, text=text)

        comment_post = PostComment.objects.create(post=post, comment=comment)

        messages.add_message(self.request, messages.SUCCESS, "comment created!")
        return redirect('club_feed_post', club_id=club.id, post_id=post.id)
