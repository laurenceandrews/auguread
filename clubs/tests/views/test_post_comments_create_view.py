"""Tests of the post comments create view."""

from clubs.forms import PostForm
from clubs.models import Club, Post, PostComment, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse


class PostCommentCreateViewTest(TestCase):
    """Tests of the comment create view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_clubs.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_book.json',
        'clubs/tests/fixtures/other_books.json',
        'clubs/tests/fixtures/seven_pos_ratings.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(pk=1)
        self.club = Club.objects.get(pk=6)

        self.post = Post.objects.create(author=self.user, text='A post made for testing.')

        self.data = {'text': 'A comment made for testing.'}
        self.url = reverse('club_feed_post_create', kwargs={'club_id': self.club.id, 'post_id': self.post.id})

    def test_create_comment_url(self):
        self.assertEqual(self.url, f'/club/{self.club.id}/feed/post/{self.post.id}/create')

    def test_get_create_comment_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_create_comment_redirects_when_not_a_club_member_or_owner(self):
        self._create_club_owner_members_and_applicants()
        self.client.login(email=self.applicant.email, password='Password123')
        post_count_before = Post.objects.count()
        comment_count_before = PostComment.objects.count()
        response = self.client.get(self.url)
        redirect_url = reverse('club_detail', kwargs={'club_id': self.club.id})
        response = self.client.post(self.url, self.data, follow=True)
        self.assertTemplateUsed(response, 'club_detail.html')
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        post_count_after = Post.objects.count()
        comment_count_after = PostComment.objects.count()
        self.assertEqual(post_count_after, post_count_before)
        self.assertEqual(comment_count_after, comment_count_before)

    def test_successful_create_comment(self):
        self.client.login(email=self.user.email, password="Password123")
        post_count_before = Post.objects.count()
        comment_count_before = PostComment.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        post_count_after = Post.objects.count()
        comment_count_after = PostComment.objects.count()
        self.assertEqual(post_count_after, post_count_before + 1)
        self.assertEqual(comment_count_after, comment_count_before + 1)

    def _create_club_owner_members_and_applicants(self):
        self.club_owner = self.club.owner
        self.applicant = User.objects.get(pk=2)
        self.club.applied_by(self.applicant)
        self.club_applicants = self.club.applicants
        self.member = User.objects.get(pk=3)
        self.club.applied_by(self.member)
        self.club.accept(self.member)
        self.club_members = self.club.members
