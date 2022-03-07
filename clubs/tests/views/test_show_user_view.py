"""Unit tests for the show user"""

from clubs.models import Club, Post, User
from clubs.tests.helpers import create_posts, reverse_with_next

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from with_asserts.mixin import AssertHTMLMixin
from clubs.models import Club

class ShowUserTest(TestCase, AssertHTMLMixin):

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(id=6)
        self.user = Club.objects.get(id=6).owner
        self.target_user = Club.objects.get(id=6).owner
        self.url = reverse('show_user', kwargs={'user_id': self.target_user.id, 'club_id': self.club.id})

    def test_show_user_url(self):
        self.assertEqual(self.url, f'/{self.club.id}/user/{self.target_user.id}')


    # def test_get_show_user_with_valid_id(self):
    #     self.client.login(email=self.user.email, password='Password123')
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'show_user.html')
    #     self.assertContains(response, "Jane Doe")
    #     self.assertContains(response, "janedoe@example.org")
    #     followable = response.context['followable']
    #     self.assertTrue(followable)
    #     follow_toggle_url = reverse('follow_toggle', kwargs={'user_id': self.target_user.id})
    #     query = f'.//form[@action="{follow_toggle_url}"]//button'
    #     with self.assertHTML(response) as html:
    #         button = html.find(query)
    #         self.assertEquals(button.text, "Follow")
    #     self.user.toggle_follow(self.target_user)
    #     response = self.client.get(self.url)
    #     with self.assertHTML(response) as html:
    #         button = html.find(query)
    #         self.assertEquals(button.text, "Unfollow")

    # def test_get_show_user_with_own_id(self):
    #     self.client.login(email=self.user.email, password='Password123')
    #     url = reverse('show_user', kwargs={'user_id': self.user.id})
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'show_user.html')
    #     self.assertContains(response, "John Doe")
    #     self.assertContains(response, "johndoe@example.org")
    #     followable = response.context['followable']
    #     self.assertFalse(followable)
    #     follow_toggle_url = reverse('follow_toggle', kwargs={'user_id': self.target_user.id})
    #     query = f'.//form[@action="{follow_toggle_url}"]//button'
    #     with self.assertHTML(response) as html:
    #         button = html.find(query)
    #         self.assertIsNone(button)

    # def test_get_show_user_with_invalid_id(self):
    #     self.client.login(email=self.user.email, password='Password123')
    #     url = reverse('show_user', kwargs={'user_id': self.user.id+9999})
    #     response = self.client.get(url, follow=True)
    #     response_url = reverse('user_list')
    #     self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
    #     self.assertTemplateUsed(response, 'user_list.html')

    # def test_get_show_user_redirects_when_not_logged_in(self):
    #     redirect_url = reverse_with_next('log_in', self.url)
    #     response = self.client.get(self.url)
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    # def test_show_user_displays_posts_belonging_to_the_shown_user_only(self):
    #     self.client.login(email=self.user.email, password='Password123')
    #     other_user = User.objects.get(email='janedoe@example.org')
    #     create_posts(other_user, 100, 103)
    #     create_posts(self.user, 200, 203)
    #     url = reverse('show_user', kwargs={'user_id': other_user.id})
    #     response = self.client.get(url)
    #     for count in range(100, 103):
    #         self.assertContains(response, f'Post__{count}')
    #     for count in range(200, 203):
    #         self.assertNotContains(response, f'Post__{count}')
    #     self.assertFalse(response.context['is_paginated'])

    # def test_show_user_displays_posts_with_pagination(self):
    #     self.client.login(email=self.user.email, password='Password123')
    #     other_user = User.objects.get(email='janedoe@example.org')
    #     create_posts(other_user, 100, 100+(settings.POSTS_PER_PAGE * 2)+3)
    #     url = reverse('show_user', kwargs={'user_id': other_user.id})
    #     response = self.client.get(url)
    #     self.assertEqual(len(response.context['posts']), settings.POSTS_PER_PAGE)
    #     self.assertTrue(response.context['is_paginated'])
    #     page_obj = response.context['page_obj']
    #     self.assertFalse(page_obj.has_previous())
    #     self.assertTrue(page_obj.has_next())
    #     page_one_url = url + '?page=1'
    #     response = self.client.get(page_one_url)
    #     self.assertEqual(len(response.context['posts']), settings.POSTS_PER_PAGE)
    #     self.assertFalse(page_obj.has_previous())
    #     page_obj = response.context['page_obj']
    #     self.assertTrue(page_obj.has_next())
    #     page_two_url = url + '?page=2'
    #     response = self.client.get(page_two_url)
    #     self.assertEqual(len(response.context['posts']), settings.POSTS_PER_PAGE)
    #     page_obj = response.context['page_obj']
    #     self.assertTrue(page_obj.has_previous())
    #     self.assertTrue(page_obj.has_next())
    #     page_three_url = url + '?page=3'
    #     response = self.client.get(page_three_url)
    #     self.assertEqual(len(response.context['posts']), 3)
    #     page_obj = response.context['page_obj']
    #     self.assertTrue(page_obj.has_previous())
    #     self.assertFalse(page_obj.has_next())

    fixtures = [
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/club.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.owner = Club.objects.get(id=1).owner
        self.owner = Club.objects.get(id=1).owners.all()[0]
        self.member = Club.objects.get(id=1).members.all()[0]
        self.url = reverse('show_user', kwargs={
                           'club_id': self.club.id, 'user_id': self.owner.id})

    def test_show_user(self):
        self.client.login(email=self.owner.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_user.html')

    def test_show_user_with_not_exists_user(self):
        self.client.login(email=self.owner.email, password="Password123")
        url = reverse('show_user', kwargs={
                      'club_id': self.club.id, 'user_id': 1000})
        response = self.client.get(url)
        redirect_url = reverse('user_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)
