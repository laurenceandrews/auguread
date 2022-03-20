"""Unit tests for the show user"""

from clubs.models import Club, Post, User
from clubs.tests.helpers import create_posts, reverse_with_next
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from schedule.models import Calendar, Event, Rule
from with_asserts.mixin import AssertHTMLMixin


class ShowUserTest(TestCase, AssertHTMLMixin):

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_rules.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.calendar = Calendar.objects.get(pk=5)
        self.club = Club.objects.get(pk=6)
        self.target_user = User.objects.get(username='@janedoe')
        self.url = reverse('show_user', kwargs={'club_id': self.club.id, 'user_id': self.target_user.id})

    def test_show_user_url(self):
        self.assertEqual(self.url, f'/{self.club.id}/user/{self.target_user.id}')

    def test_show_user(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user.html')

    def test_get_show_user_with_valid_id(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user.html')
        # target_user = response.context['target']
        # self.assertEqual(target_user, self.target_user)
        # self.assertContains(response, "Jane Doe")
        # self.assertContains(response, "@janedoe")
        # self.assertContains(response, "janedoe@example.org")
        # followable = response.context['followable']
        # self.assertTrue(followable)
        # follow_toggle_url = reverse('follow_toggle', kwargs={'club_id': self.club.id, 'user_id': self.target_user.id})
        # query = f'.//form[@action="{follow_toggle_url}"]//button'
        # with self.assertHTML(response) as html:
        #     button = html.find(query)
        #     self.assertEquals(button.text, "Follow")
        # self.user.toggle_follow(self.target_user)
        # response = self.client.get(self.url)
        # with self.assertHTML(response) as html:
        #     button = html.find(query)
        #     self.assertEquals(button.text, "Unfollow")

    def test_get_show_user_with_own_id(self):
        self.client.login(email=self.user.email, password='Password123')
        url = reverse('show_user', kwargs={'club_id': self.club.id, 'user_id': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user.html')
        target_user = response.context['target']
        self.assertEqual(target_user, self.user)
        self.assertContains(response, "John Doe")
        self.assertContains(response, "johndoe@example.org")
        followable = response.context['followable']
        self.assertFalse(followable)
        follow_toggle_url = reverse('follow_toggle', kwargs={'user_id': self.target_user.id})
        query = f'.//form[@action="{follow_toggle_url}"]//button'
        with self.assertHTML(response) as html:
            button = html.find(query)
            self.assertIsNone(button)

    def test_get_show_user_with_invalid_id(self):
        self.client.login(email=self.user.email, password='Password123')
        url = reverse('show_user', kwargs={'club_id': self.club.id, 'user_id': self.user.id + 9999})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_list.html')

    def test_get_show_user_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_show_user_displays_posts_belonging_to_the_shown_user_only(self):
        self.client.login(email=self.user.email, password='Password123')
        self._create_test_posts_short()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user.html')
        self.assertEqual(len(response.context['posts']), 2)

    def test_show_user_displays_posts_with_pagination(self):
        self.client.login(email=self.user.email, password='Password123')
        self._create_test_posts_long()
        url = reverse('show_user', kwargs={'club_id': self.club.id, 'user_id': self.target_user.id})
        response = self.client.get(self.url)
        self.assertEqual(Post.objects.all().count(), 40)
        # self.assertEqual(len(response.context['posts']), settings.POSTS_PER_PAGE)
        # self.assertTrue(response.context['is_paginated'])
        # page_obj = response.context['page_obj']
        # self.assertFalse(page_obj.has_previous())
        # self.assertTrue(page_obj.has_next())
        # page_one_url = url + '?page=1'
        # response = self.client.get(page_one_url)
        # self.assertEqual(len(response.context['posts']), settings.POSTS_PER_PAGE)
        # self.assertFalse(page_obj.has_previous())
        # page_obj = response.context['page_obj']
        # self.assertTrue(page_obj.has_next())
        # page_two_url = url + '?page=2'
        # response = self.client.get(page_two_url)
        # self.assertEqual(len(response.context['posts']), settings.POSTS_PER_PAGE)
        # page_obj = response.context['page_obj']
        # self.assertTrue(page_obj.has_previous())
        # self.assertTrue(page_obj.has_next())
        # page_three_url = url + '?page=3'
        # response = self.client.get(page_three_url)
        # self.assertEqual(len(response.context['posts']), 3)
        # page_obj = response.context['page_obj']
        # self.assertTrue(page_obj.has_previous())
        # self.assertFalse(page_obj.has_next())

    def _create_test_posts_short(self):
        data = {
            'author': self.user,
            'text': 'My first post.'
        }
        post = Post(**data)
        post.save()

        data = {
            'author': self.user,
            'text': 'My second post.'
        }
        post = Post(**data)
        post.save()

        data = {
            'author': self.target_user,
            'text': 'My first post.'
        }
        post = Post(**data)
        post.save()

        data = {
            'author': self.target_user,
            'text': 'My second post.'
        }
        post = Post(**data)
        post.save()

    def _create_test_posts_long(self):
        for num in range(1, 21):
            data = {
                'author': self.user,
                'text': 'My post: ' + str(num)
            }
            post = Post(**data)
            post.save()

        for num in range(1, 21):
            data = {
                'author': self.target_user,
                'text': 'My post: ' + str(num)
            }
            post = Post(**data)
            post.save()

    def test_show_user_with_not_exists_user(self):
        self.client.login(email=self.user.email, password="Password123")
        url = reverse('show_user', kwargs={
                      'club_id': self.club.id, 'user_id': 1000})
        response = self.client.get(url)
        redirect_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)
