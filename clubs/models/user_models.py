
from pickle import FALSE

from clubs.models.book_models import Book
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
from django_countries.fields import CountryField
from libgravatar import Gravatar
from schedule.models import Calendar, Event, Rule


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
        app_label = "clubs"
        verbose_name = "User"
        verbose_name_plural = "Users"
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

    def clubs_attended(self):
        """Return all clubs user is either a member, officer or owner of."""
        club_ids = Club_Users.objects.filter(user=self).exclude(role_num="1").values_list('club', flat=True)
        return Club.objects.filter(id__in=club_ids)

    def is_applicant(self, club):
        return self.membership_type(club) == 'Applicant'

    def is_owner(self, club):
        return self.membership_type(club) == 'Owner'

    def is_member(self, club):
        return self.membership_type(club) == 'Member'

    def membership_type(self, club):
        """Type of membership the user has"""
        club_user = Club_Users.objects.get(user=self, club=club)
        if club_user.role_num == "4":
            return 'Owner'
        elif club_user.role_num == "3":
            return 'Officer'
        elif club_user.role_num == "2":
            return 'Member'
        else:
            return 'Applicant'

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

    def friends_list(self):
        """Returns the users self is following."""
        return self.followees.all()


class Club(models.Model):
    """Club model used for all the functions of a club."""
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

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=FALSE
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

    class Meta:
        """Model options"""
        app_label = "clubs"
        verbose_name = "Club"
        verbose_name_plural = "Clubs"
        ordering = ['name']

    def applicants(self):
        """Return all users who are applicants of this club."""
        club_applicants_ids = Club_Users.objects.filter(club=Club.objects.get(id=self.id), role_num='1').values_list('user', flat=True)
        return User.objects.filter(id__in=club_applicants_ids)

    def members(self):
        """Return all users who are members of this club."""
        club_members_ids = Club_Users.objects.filter(club=Club.objects.get(id=self.id), role_num='2').values_list('user', flat=True)
        return User.objects.filter(id__in=club_members_ids)

    def officers(self):
        """Return all users who are officers of this club."""
        club_officers_ids = Club_Users.objects.filter(club=Club.objects.get(id=self.id), role_num='3').values_list('user', flat=True)
        return User.objects.filter(id__in=club_officers_ids)

    def owners(self):
        """Return all users who are owners of this club."""
        club_owners_ids = Club_Users.objects.filter(club=Club.objects.get(id=self.id), role_num='4').values_list('user', flat=True)
        return User.objects.filter(id__in=club_owners_ids)

    def accept(self, user):
        club_user = Club_Users.objects.get(club=Club.objects.get(id=self.id), user=user)
        club_user.role_num = 2
        club_user.save()

    def applied_by(self, user):
        if not Club_Users.objects.filter(club=Club.objects.get(id=self.id), user=user).exists():
            Club_Users.objects.create(club=Club.objects.get(id=self.id), user=user)

    def in_club(self, user):
        if user in self.members() or user in self.owners() or user in self.applicants() or user == self.owner:
            return True
        else:
            return False

    def transfer(self, user):
        """Transfer ownership of the club to another owner"""
        owner = self.owner
        club = Club.objects.get(id=self.id)
        old_owner_club_user = Club_Users.objects.get(club=club, role_num="4")
        new_owner_club_user = Club_Users.objects.get(club=Club.objects.get(id=self.id), user=user)
        if new_owner_club_user.user in self.members():
            old_owner_club_user.role_num = 2
            old_owner_club_user.save()
            new_owner_club_user.role_num = 4
            new_owner_club_user.save()
            self.owner = new_owner_club_user.user
            self.save()

    def favourite_books(self):
        """Return all favourite books of this club."""
        club_books_ids = Club_Books.objects.filter(club=Club.objects.get(id=self.id)).values_list('book', flat=True)
        return Book.objects.filter(id__in=club_books_ids)

    def currently_reading(self):
        """Return the club's currently reading book, or None."""
        currently_reading = None
        club_book_history_exists = Club_Book_History.objects.filter(club=Club.objects.get(id=self.id)).exists()
        if club_book_history_exists:
            club_book_history = Club_Book_History.objects.filter(club=Club.objects.get(id=self.id)).last()
            currently_reading = club_book_history.book
        return currently_reading


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

    APPLICANT = '1'
    MEMBER = '2'
    OFFICER = '3'
    OWNER = '4'
    ROLE_NUM_CHOICES = [
        (APPLICANT, 'Applicant'),
        (MEMBER, 'Member'),
        (OFFICER, 'Officer'),
        (OWNER, 'Owner')
    ]
    role_num = models.CharField(
        max_length=1,
        choices=ROLE_NUM_CHOICES,
        default=1,
        blank=False
    )

    class Meta:
        app_label = "clubs"
        verbose_name = "Club"
        verbose_name_plural = "Club User"


class Book_Rating(models.Model):
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

    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        blank=False,
        default=1
    )

    BOOK_RATING_CHOICES = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10'),
    ]

    rating = models.CharField(
        max_length=9,
        choices=BOOK_RATING_CHOICES,
        blank=False
    )

    class Meta:
        app_label = "clubs"
        verbose_name = "User Book Rating"
        verbose_name_plural = "User Book Ratings"


class User_Book_History(models.Model):
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

    class Meta:
        app_label = "clubs"
        verbose_name = "User Book History"
        verbose_name_plural = "User Book Histories"


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

    class Meta:
        app_label = "clubs"
        verbose_name = "User Favourite Book"
        verbose_name_plural = "User Favourite Books"


class User_Clubs(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        default=0
    )

    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        blank=False,
        default=0
    )

    class Meta:
        app_label = "clubs"
        verbose_name = "User Recommended Club"
        verbose_name_plural = "User Recommended Clubs"


class Club_Book_History(models.Model):
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

    average_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        blank=False,
        default=None
    )

    class Meta:
        app_label = "clubs"
        verbose_name = "Club Book History"
        verbose_name_plural = "Club Book Histories"


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

    class Meta:
        app_label = "clubs"
        verbose_name = "Club Favourite Book"
        verbose_name_plural = "Club Favourite Books"
