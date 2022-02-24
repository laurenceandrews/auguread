from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club
from clubs.tests.helpers import reverse_with_next

class UserListTestCase(TestCase):

    fixtures = ['clubs/tests/fixtures/club.json']

    # def setUp(self):
    #     self.club = Club.objects.get(id=1)
    #     self.url = reverse('user_list', kwargs={'club_id': self.club.id})
    #     self.member_user = Club.objects.get(id=1).members.all()[0]
    #     self.owner_user = Club.objects.get(id=1).owners.all()[0]
    #     self.applicant_user = Club.objects.get(id=1).applicants.all()[0]
    #
    # def test_user_list_url(self):
    #     self.assertEqual(self.url, '/1/users')
    #
    # def test_get_user_list(self):
    #     self.client.login(email=self.member_user.email, password="Password123")
    #     self._create_test_users(settings.NUMBER_PER_PAGE)
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'user_list.html')
    #     self.assertEqual(
    #         len(response.context['users']), settings.NUMBER_PER_PAGE - 2)

    # def test_get_user_list(self):
    #     self.client.login(email=self.user.email, password='Password123')
    #     self._create_test_users(settings.USERS_PER_PAGE-1)
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'user_list.html')
    #     self.assertEqual(len(response.context['users']), settings.USERS_PER_PAGE)
    #     self.assertFalse(response.context['is_paginated'])
    #     for user_id in range(settings.USERS_PER_PAGE-1):
    #         self.assertContains(response, f'@user{user_id}')
    #         self.assertContains(response, f'First{user_id}')
    #         self.assertContains(response, f'Last{user_id}')
    #         user = User.objects.get(email=f'@user{user_id}')
    #         user_url = reverse('show_user', kwargs={'user_id': user.id})
    #         self.assertContains(response, user_url)

    # def test_get_user_list_with_pagination(self):
    #     self.client.login(email=self.user.email, password='Password123')
    #     self._create_test_users(settings.USERS_PER_PAGE*2+3-1)
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'user_list.html')
    #     self.assertEqual(len(response.context['users']), settings.USERS_PER_PAGE)
    #     self.assertTrue(response.context['is_paginated'])
    #     page_obj = response.context['page_obj']
    #     self.assertFalse(page_obj.has_previous())
    #     self.assertTrue(page_obj.has_next())
    #     page_one_url = reverse('user_list') + '?page=1'
    #     response = self.client.get(page_one_url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'user_list.html')
    #     self.assertEqual(len(response.context['users']), settings.USERS_PER_PAGE)
    #     page_obj = response.context['page_obj']
    #     self.assertFalse(page_obj.has_previous())
    #     self.assertTrue(page_obj.has_next())
    #     page_two_url = reverse('user_list') + '?page=2'
    #     response = self.client.get(page_two_url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'user_list.html')
    #     self.assertEqual(len(response.context['users']), settings.USERS_PER_PAGE)
    #     page_obj = response.context['page_obj']
    #     self.assertTrue(page_obj.has_previous())
    #     self.assertTrue(page_obj.has_next())
    #     page_three_url = reverse('user_list') + '?page=3'
    #     response = self.client.get(page_three_url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'user_list.html')
    #     self.assertEqual(len(response.context['users']), 3)
    #     page_obj = response.context['page_obj']
    #     self.assertTrue(page_obj.has_previous())
    #     self.assertFalse(page_obj.has_next())


    # def test_get_user_list_redirects_when_not_logged_in(self):
    #     redirect_url = reverse_with_next('log_in', self.url)
    #     response = self.client.get(self.url)
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def _create_test_users(self, user_count):
        for user_id in range(user_count):
            User.objects.create_user(f'@user{user_id}',
                email=f'user{user_id}@test.org',
                password='Password123',
                first_name=f'First{user_id}',
                last_name=f'Last{user_id}',
                bio=f'Bio {user_id}',
            )
