"""Tests of the post comments view."""
from clubs.forms import PostForm
from clubs.models import Club, Post, PostComment, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse


class ClubFeedViewTestCase(TestCase):
    """Tests of the post comments view."""

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
        self.user = User.objects.get(pk=1)
        self.club = Club.objects.get(pk=6)
        self.post = Post.objects.create(author=self.user, text='A post made for testing.')
        self.url = reverse('club_feed_post', kwargs={'club_id': self.club.id, 'post_id': self.post.id})

    def test_feed_url(self):
        self.assertEqual(self.url, f'/club/{self.club.id}/feed/post/{self.post.id}')

    def test_get_feed(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'post_comments.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PostForm))
        self.assertFalse(form.is_bound)

    def test_get_feed_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_feed_redirects_when_not_a_club_member_or_owner(self):
        self._create_club_owner_members_and_applicants()
        self.client.login(email=self.applicant.email, password='Password123')
        post_count_before = Post.objects.count()
        club_feed_post_count_before = PostComment.objects.count()
        response = self.client.get(self.url)
        redirect_url = reverse('club_detail', kwargs={'club_id': self.club.id})
        response = self.client.post(self.url, follow=True)
        self.assertTemplateUsed(response, 'club_detail.html')
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        post_count_after = Post.objects.count()
        club_feed_post_count_after = PostComment.objects.count()
        self.assertEqual(post_count_after, post_count_before)
        self.assertEqual(club_feed_post_count_after, club_feed_post_count_before)

    def test_get_comments_list(self):
        self.client.login(email=self.user.email, password="Password123")
        self._create_club_owner_members_and_applicants()
        self._create_post_and_comment()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'post_comments.html')
        self.assertEqual(len(response.context['comments']), 1)
        self.assertTrue(self.comment in response.context['comments'])
        self.assertFalse(self.comment_on_other_post in response.context['comments'])
        self.assertTrue(self.post in response.context['original_post'])
        self.assertFalse(self.other_post in response.context['original_post'])

    def _create_club_owner_members_and_applicants(self):
        self.club_owner = self.club.owner
        self.applicant = User.objects.get(pk=2)
        self.club.applied_by(self.applicant)
        self.club_applicants = self.club.applicants
        self.member = User.objects.get(pk=3)
        self.club.applied_by(self.member)
        self.club.accept(self.member)
        self.club_members = self.club.members

    def _create_post_and_comment(self):
        data = {'post_text': 'A post made for testing.',
                'comment_text': 'A comment made for testing.'}

        self.comment = Post.objects.create(author=self.member, text=data['comment_text'])
        self.post_comment = PostComment.objects.create(post=self.post, comment=self.comment)

        self.other_post = Post.objects.create(author=self.club_owner, text=data['post_text'])
        self.comment_on_other_post = Post.objects.create(author=self.member, text=data['comment_text'])
        self.post_comment_on_other_post = PostComment.objects.create(post=self.other_post, comment=self.comment_on_other_post)
