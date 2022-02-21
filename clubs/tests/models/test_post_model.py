from django.core.exceptions import ValidationError
from django.test import TestCase
from clubs.models import Post, User

class PostTest(TestCase):

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')
from django_countries.fields import CountryField

class PostTest(TestCase):
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
        self.post = Post(
            author=self.user,
            text="The quick brown fox jumps over the lazy dog."
        )

    def test_valid_message(self):
        try:
            self.post.full_clean()
        except ValidationError:
            self.fail("Test message should be valid")

    def test_author_must_not_be_blank(self):
        self.post.author = None
        with self.assertRaises(ValidationError):
            self.post.full_clean()

    def test_text_must_not_be_blank(self):
        self.post.text = ''
        with self.assertRaises(ValidationError):
            self.post.full_clean()

    def test_text_must_not_be_overlong(self):
        self.post.text = 'x' * 281
        with self.assertRaises(ValidationError):
            self.post.full_clean()
