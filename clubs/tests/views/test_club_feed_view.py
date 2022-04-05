"""Tests of the club feed view."""
from clubs.forms import PostForm
from clubs.models import Club, ClubFeedPost, Post, User
from clubs.tests.helpers import reverse_with_next
from django.test import TestCase
from django.urls import reverse


class ClubFeedViewTestCase(TestCase):
    """Tests of the club feed view."""

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
        self.url = reverse('club_feed', kwargs={'club_id': self.club.id})

    def test_feed_url(self):
        self.assertEqual(self.url, f'/club/{self.club.id}/feed/')

    def test_get_feed(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_feed.html')
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
        club_feed_post_count_before = ClubFeedPost.objects.count()
        response = self.client.get(self.url)
        redirect_url = reverse('club_detail', kwargs={'club_id': self.club.id})
        response = self.client.post(self.url, follow=True)
        self.assertTemplateUsed(response, 'club_detail.html')
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        post_count_after = Post.objects.count()
        club_feed_post_count_after = ClubFeedPost.objects.count()
        self.assertEqual(post_count_after, post_count_before)
        self.assertEqual(club_feed_post_count_after, club_feed_post_count_before)

    def test_get_event_list(self):
        self.client.login(email=self.user.email, password="Password123")
        self._create_club_owner_members_and_applicants()
        self._create_club_posts()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_feed.html')
        self.assertEqual(len(response.context['posts']), 2)
        self.assertTrue(self.owner_post in response.context['posts'])
        self.assertTrue(self.member_post in response.context['posts'])
        self.assertFalse(self.non_member_now_owner_post in response.context['posts'])

    def _create_club_owner_members_and_applicants(self):
        self.club_owner = self.club.owner
        self.applicant = User.objects.get(pk=2)
        self.club.applied_by(self.applicant)
        self.club_applicants = self.club.applicants
        self.member = User.objects.get(pk=3)
        self.club.applied_by(self.member)
        self.club.accept(self.member)
        self.club_members = self.club.members

    def _create_club_posts(self):
        data = {'text': 'A post made for testing.'}
        post = Post.objects.create(author=self.club_owner, text=data['text'])
        self.owner_post = post
        ClubFeedPost.objects.create(club=self.club, post=post)

        post = Post.objects.create(author=self.member, text=data['text'])
        self.member_post = post
        ClubFeedPost.objects.create(club=self.club, post=post)

        other_club = Club.objects.get(pk=16)
        post = Post.objects.create(author=self.member, text=data['text'])
        self.non_member_now_owner_post = post
        ClubFeedPost.objects.create(club=other_club, post=post)
