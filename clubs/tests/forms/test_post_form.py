from django.test import TestCase
from clubs.models import User, Post
from clubs.forms import PostForm

class PostFormTestCase(TestCase):

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')

>>>>>>> d5fbc95ad7504937619a3dbc50ed9ae64238c528
from django_countries.fields import CountryField

class PostFormTestCase(TestCase):

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.create_user(
            '@johndoe',
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org',
            password='Password123',
            bio='The quick brown fox jumps over the lazy dog.'
            #country = Country(code = 'NZ')
        )

>>>>>>> d5fbc95ad7504937619a3dbc50ed9ae64238c528

    def test_valid_post_form(self):
        input = {'text': 'x'*200 }
        form = PostForm(data=input)
        self.assertTrue(form.is_valid())

    def test_invalid_post_form(self):
        input = {'text': 'x'*600 }
        form = PostForm(data=input)
        self.assertFalse(form.is_valid())
