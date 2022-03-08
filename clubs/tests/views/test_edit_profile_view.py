
"""Tests for the profile view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from clubs.forms import EditProfileForm
from clubs.models import User
from clubs.tests.helpers import reverse_with_next ,MenuTesterMixin

"""Test suite for the profile view."""
class UserViewTestCase(TestCase , MenuTesterMixin):

    fixtures = ['clubs/tests/fixtures/default_user.json',
            'clubs/tests/fixtures/other_users.json' ]

    def setUp(self):
        self.user = User.objects.get(email='johndoe@example.org')
        self.url = reverse("edit_user")
        self.form_input = {
            "first_name": "John2",
            "last_name": "Doe2",
            "email": "johndoe2@example.org",
            "public_bio": "New bio",
        }

    def test_profile_url(self):
        self.assertEqual(self.url, 'editprofile/' )

    def test_get_profile(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_user.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditProfileForm))
        self.assertEqual(form.instance, self.user)
        self.assert_menu(response)


    def test_get_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_unsuccesful_profile_update(self):
        self.client.login(username=self.user.email, password="Password123")
        self.form_input["email"] = "johndoe"
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_user.html")
        form = response.context["form"]
        self.assertTrue(isinstance(form, EditProfileForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "John")
        self.assertEqual(self.user.last_name, "Doe")
        self.assertEqual(self.user.email, "johndoe@example.org")
        self.assertEqual(
            self.user.public_bio, "Hello, I am John Doe."
        )
        self.assert_menu(response)



    def test_unsuccessful_profile_update_due_to_duplicate_email(self):
        self.client.login(username=self.user.email, password="Password123")
        self.form_input["email"] = "janedoe@example.org"
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_user.html")
        form = response.context["form"]
        self.assertTrue(isinstance(form, EditProfileForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "John")
        self.assertEqual(self.user.last_name, "Doe")
        self.assertEqual(self.user.email, "johndoe@example.org")
        self.assertEqual(self.user.public_bio, "Hello, I am John Doe.")
        self.assert_menu(response)

    def test_succesful_profile_update(self):
        self.client.login(username=self.user.email, password="Password123")
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse("user_profile_self")
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, "user_profile_self.html")
        messages_queryset = list(response.context["messages"])
        self.assertEqual(len(messages_queryset), 1)
        self.assertEqual(messages_queryset[0].level, messages.SUCCESS)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "John2")
        self.assertEqual(self.user.last_name, "Doe2")
        self.assertEqual(self.user.email, "johndoe2@example.org")
        self.assertEqual(self.user.public_bio, "New bio")
        self.assert_menu(response)


    def test_post_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in' , self.url)
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(
            response, redirect_url, status_code=302, target_status_code=200
        )
