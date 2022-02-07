"""Models in the clubs app."""

from pickle import FALSE
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from libgravatar import Gravatar

class User(AbstractUser):
    """User model used for authentication and authoring."""

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^@\w{3,}$',
                message='Username must consist of @ followed by at least three alphanumericals'
            )
        ]
    )

    first_name = models.CharField(
        max_length=50,
        blank=False
    )

    last_name = models.CharField(
        max_length=50,
        blank=False
    )

    email = models.EmailField(
        unique=True,
        blank=False
    )

    bio = models.CharField(
        max_length=520,
        blank=True
    )

    class Meta:
        """Model options"""
        ordering = ['first_name', 'last_name']

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)

    def membership_type(self, club):
        """Type of membership the user has"""
        if self == club.owner:
            return 'Owner'
        elif self in club.members.all():
            return 'Member'
        else:
            return 'User'

    def is_owner(self, club):
        return self.membership_type(club) == 'Owner'

    def is_member(self, club):
        return self.membership_type(club) == 'Member'

class Book(models.Model):
    ISBN = models.CharField(
        max_length = 10,
        blank = False
    )

    title = models.CharField(
        max_length = 250,
        blank = False
    )
    
    author = models.CharField(
        max_length = 300,
        blank = False
    )
    
    publisher = models.CharField(
        max_length = 300,
        blank = False
    )
    
    publication_year = models.IntegerField(
        blank = False
    )

class Post(models.Model):
    """Posts by users."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    text = models.CharField(
        max_length=280
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        """Model options."""
        ordering = ['-created_at']

class Club(models.Model):
    name = models.CharField(
        max_length=50,
        blank=False,
        unique=True
    )

    location = models.CharField(
        max_length=500,
        blank=False
    )

    description = models.CharField(
        max_length=520,
        blank=False
    )

    # A foreign key is not required for the club owner
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=FALSE
    )

    members = models.ManyToManyField(
        User,
        through='club_users',
        related_name='member',
        blank=True
    )

    books = models.ManyToManyField(
        Book,
        through='club_books',
        related_name='book',
        blank=True
    )

    # measured in words per minute (average for all club members)
    avg_reading_speed = models.IntegerField(
        validators=[
            MinValueValidator(50),
            MaxValueValidator(500)
        ],
        blank=False,
        default=200  #if reading speed test not completed
    )

    # favourite_books = models.ManyToManyField(
    #
    # )
    class Meta:
        """Model options"""
        ordering = ['name']

    def in_club(self, user):
        if user in self.members.all() or user == self.owner:
            return True
        else:
            return False

class Club_Users(models.Model):
    club_id = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        blank=False,
        default=0
    )

    user_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        default=0
    )

    role_num = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        blank=False,
        default=1
    )

class Club_Books(models.Model):
    club_id = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        blank=False,
        default=0
    )

    book_id = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        blank=False,
        default=0
    )