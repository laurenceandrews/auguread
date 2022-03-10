"""Models in the clubs app."""

import uuid
from pickle import FALSE

from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
from django_countries.fields import CountryField
from libgravatar import Gravatar
from schedule.models import Calendar, Event, Rule

from django import forms


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

    id = models.AutoField(primary_key=True)

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
            MaxValueValidator(105),
            MinValueValidator(5)
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

    city = models.CharField(
        max_length=50,
        blank=False
    )

    country = CountryField(
        blank_label='(select country)'
    )

    followers = models.ManyToManyField(
        'self', symmetrical=False, related_name='followees'
    )

    class Meta:
        """Model options"""
        ordering = ['first_name', 'last_name']

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def location(self):
        return f'{self.city}, {self.country}'

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
        if self == club.owners.all():
            return 'Owner'
        elif self in club.members.all():
            return 'Member'
        elif self in club.applicants.all():
            return 'Applicant'
        else:
            return 'User'

    def clubs_attended(self):
        return list(self.member.all()) + list(self.owner.all()) + list(Club.objects.filter(owner=self))

    def toggle_follow(self, followee):
        """Toggles whether self follows the given followee."""

        if followee == self:
            return
        if self.is_following(followee):
            self._unfollow(followee)
        else:
            self._follow(followee)

    def _follow(self, user):
        user.followers.add(self)

    def _unfollow(self, user):
        user.followers.remove(self)

    def is_following(self, user):
        """Returns whether self follows the given user."""
        return user in self.followees.all()

    def follower_count(self):
        """Returns the number of followers of self."""
        return self.followers.count()

    def followee_count(self):
        """Returns the number of followees of self."""
        return self.followees.count()


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

    image_small = models.ImageField(
        blank=False,
        default='/static/default_book.png/'
    )

    image_medium = models.ImageField(
        blank=False,
        default='/static/default_book.png/'
    )
    
    image_large = models.ImageField(
        blank=False,
        default='/static/default_book.png/'
    )

    rating = models.IntegerField(
        blank=False,
        default=0
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


class MeetingLink(models.Model):
    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE
    )

    meeting_link = models.URLField(
        blank=False
    )


class Address(models.Model):
    name = models.CharField(
        "Full name",
        max_length=1024,
    )

    address1 = models.CharField(
        "Address line 1",
        max_length=1024,
    )

    address2 = models.CharField(
        "Address line 2",
        max_length=1024,
        blank=True
    )

    zip_code = models.CharField(
        "ZIP / Postal code",
        max_length=12,
        blank=True
    )

    city = models.CharField(
        "City",
        max_length=1024,
    )

    country = CountryField(
        blank_label='(select country)'
    )

    def __str__(self):
        return self.name

    def full_address(self):
        return f'{self.name}. {self.zip_code}, {self.address1}, {self.address2}. {self.city}, {self.country}.'


class MeetingAddress(models.Model):
    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE
    )

    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        blank=FALSE
    )

    class Meta:
        verbose_name = "Meeting Address"
        # verbose_name_plural = "Meeting Addresses"


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

    calendar = models.OneToOneField(
        Calendar,
        on_delete=models.CASCADE
    )

    ONLINE = 'ONL'
    IN_PERSON = 'INP'
    MEETING_TYPE_CHOICES = [
        (ONLINE, 'Online'),
        (IN_PERSON, 'In-person')
    ]
    meeting_type = models.CharField(
        max_length=3,
        choices=MEETING_TYPE_CHOICES,
        default=IN_PERSON,
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
        User, through='MemberMembership', related_name='member', blank=True)
    owners = models.ManyToManyField(
        User, through='OwnerMembership', related_name='owner', blank=True)

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

    def transfer(self, user):
        owner = self.owner
        if user in self.owners.all():
            self.owners.add(owner)
            self.owner = user
            self.owners.remove(user)
            self.save()


class ApplicantMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)


class OwnerMembership(models.Model):
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

class BookRatingForm(forms.Form):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    previous_rating = Book.rating
    rating = forms.ChoiceField(
        required = False,
        label = 'Rate book',
        initial = 'previous_rating',
        error_messages = {},
        choices=[("*", "No rating")] + [(x, x) for x in range(1, 11)],
    )