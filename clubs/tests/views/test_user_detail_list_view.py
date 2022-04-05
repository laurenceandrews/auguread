from clubs.models import Club, User
from clubs.tests.helpers import reverse_with_next
from django.conf import settings
from django.test import TestCase
from django.urls import reverse


class UserDetailListTestCase(TestCase):

    fixtures = ['clubs/tests/fixtures/default_user.json',
                'clubs/tests/fixtures/default_book.json',
                'clubs/tests/fixtures/other_books.json',
                'clubs/tests/fixtures/seven_pos_ratings.json'
                ]

    def setUp(self):
        self.url = reverse('user_detail_list')
        self.user = User.objects.get(email='johndoe@example.org')
        self.user = User.objects.get(username='@johndoe')

    def test_user_detail_list_url(self):
        self.assertEqual(self.url, '/users/')

    def test_get_user_list(self):
        self.client.login(email=self.user.email, password='Password123')
        self._create_test_users(settings.USERS_PER_PAGE - 1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_detail_list.html')
        self.assertEqual(len(response.context['users']), settings.USERS_PER_PAGE)
        self.assertFalse(response.context['is_paginated'])
        for user_id in range(settings.USERS_PER_PAGE - 1):
            self.assertContains(response, f'@user{user_id}')
            self.assertContains(response, f'First{user_id}')
            self.assertContains(response, f'Last{user_id}')
            user = User.objects.get(username=f'@user{user_id}')
            user_url = reverse('user_detail', kwargs={'user_id': user.id})
            self.assertContains(response, user_url)

    def test_get_user_list_with_pagination(self):
        self.client.login(email=self.user.email, password='Password123')
        self._create_test_users(settings.USERS_PER_PAGE * 2 + 3 - 1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_detail_list.html')
        self.assertEqual(len(response.context['users']), settings.USERS_PER_PAGE)
        self.assertTrue(response.context['is_paginated'])
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_one_url = reverse('user_detail_list') + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_detail_list.html')
        self.assertEqual(len(response.context['users']), settings.USERS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_two_url = reverse('user_detail_list') + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_detail_list.html')
        self.assertEqual(len(response.context['users']), settings.USERS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_three_url = reverse('user_detail_list') + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_detail_list.html')
        self.assertEqual(len(response.context['users']), 3)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())

    def test_get_user_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def _create_test_users(self, user_count=10):
        for user_id in range(user_count):
            User.objects.create_user(email=f'user{user_id}@test.org',
                                     username=f'@user{user_id}',
                                     password='Password123',
                                     first_name=f'First{user_id}',
                                     last_name=f'Last{user_id}',
                                     bio=f'Bio {user_id}',
                                     )
