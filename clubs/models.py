"""Models in the clubs app."""

import uuid
from pickle import FALSE

from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
from django_countries.fields import CountryField
from libgravatar import Gravatar


class UserManager(UserManager):
    """ User Manager that knows how to create users via email instead of username """

    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra_fields)

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """User model used for authentication and authoring."""
    objects = UserManager()
    REQUIRED_FIELDS = []
    USERNAME_FIELD = "email"
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

    id = models.CharField(
        primary_key=True,
        max_length=20
    )

    first_name = models.CharField(
        max_length=50,
        blank=False
    )

    last_name = models.CharField(
        max_length=50,
        blank=False
    )

    age = models.PositiveIntegerField(
        default=18,
        validators=[
            MaxValueValidator(150),
            MinValueValidator(1)
        ]
    )

    email = models.EmailField(
        unique=True,
        blank=False
    )

    bio = models.CharField(
        max_length=520,
        blank=True
    )

    country = CountryField(
        blank_label='(select country)'
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

    def is_applicant(self, club):
        return self.membership_type(club) == 'Applicant'

    def is_owner(self, club):
        return self.membership_type(club) == 'Owner'

    def is_member(self, club):
        return self.membership_type(club) == 'Member'

    def membership_type(self, club):
        """Type of membership the user has"""
        if self == club.owner:
            return 'Owner'
        elif self in club.members.all():
            return 'Member'
        elif self in club.applicants.all():
            return 'Applicant'
        else:
            return 'User'

    def clubs_attended(self):
        return list(self.member.all()) + list(self.owner.all()) + list(Club.objects.filter(owner=self))


class Book(models.Model):
    ISBN = models.CharField(
        max_length=10,
        blank=False
    )

    title = models.CharField(
        max_length=250,
        blank=False
    )

    author = models.CharField(
        max_length=300,
        blank=False
    )

    publisher = models.CharField(
        max_length=300,
        blank=False
    )

    publication_year = models.IntegerField(
        blank=False
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

    applicants = models.ManyToManyField(
        User, through='ApplicantMembership', related_name='applicant', blank=True)

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
        default=200  # if reading speed test not completed
    )

    # favourite_books = models.ManyToManyField(
    #
    # )
    class Meta:
        """Model options"""
        ordering = ['name']

    def member_list(self):
        return self.members.all()

    def applicant_list(self):
        return self.applicants.all()

    def owner_list(self):
        return self.owners.all()

    def accept(self, user):
        self.members.add(user)
        self.applicants.remove(user)

    def applied_by(self, user):
        self.applicants.add(user)

    def in_club(self, user):
        if user in self.members.all() or user in self.owners.all() or user in self.applicants.all() or user == self.owner:
            return True
        else:
            return False

class ApplicantMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)

class Club_Users(models.Model):
    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        blank=False,
        default=0
    )

    user = models.ForeignKey(
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
    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        blank=False,
        default=0
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        blank=False,
        default=0
    )


class User_Books(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        default=0
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        blank=False,
        default=0
    )


class MyUUIDModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
