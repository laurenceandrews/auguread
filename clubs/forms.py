"""Forms for the book club app"""


import datetime

from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField
from schedule.models import Calendar, Event, Rule

from .models import Address, Club, MeetingAddress, MeetingLink, Post, User


class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    email = forms.CharField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticated user if possible."""

        user = None
        if self.is_valid():
            email = self.cleaned_data.get('email')
            password = self.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
        return user


class NewPasswordMixin(forms.Form):
    """Form mixin for new_password and password_confirmation fields."""

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
        )]
    )
    password_confirmation = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """ Ensure that new_password and password_confirmation contain the same password."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation',
                           'Confirmation does not match password.')


class PasswordForm(NewPasswordMixin):
    """Form enabling users to change their password."""

    password = forms.CharField(
        label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        """Construct new form instance with a user instance."""
        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        password = self.cleaned_data.get('password')
        if self.user is not None:
            user = authenticate(email=self.user.email, password=password)
        else:
            user = None

        if user is None:
            self.add_error('password', "Password is invalid")

    def save(self):
        """Save the user's new password."""

        new_password = self.cleaned_data['new_password']
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user


class SignUpForm(NewPasswordMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'age', 'username', 'email', 'bio', 'city', 'country']
        widgets = {'bio': forms.Textarea()}

    country = CountryField(blank_label='(Select country)').formfield()

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[
            RegexValidator(
                regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
                message='Password must contain an uppercase character, a lowercase character and a number.'
            ),
        ],
    )
    password_confirmation = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput(),
    )

    def clean(self):
        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

    def save(self):
        super().save(commit=False)
        user = User.objects.create_user(
            username=self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            age=self.cleaned_data.get('age'),
            email=self.cleaned_data.get('email'),
            bio=self.cleaned_data.get('bio'),
            city=self.cleaned_data.get('city'),
            country=self.cleaned_data.get('country'),
            password=self.cleaned_data.get('new_password'),
        )
        return user


class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'bio']
        widgets = {'bio': forms.Textarea()}


class PostForm(forms.ModelForm):
    """Form to ask user for post text.

    The post author must be by the post creator.
    """

    class Meta:
        """Form options."""

        model = Post
        fields = ['text']
        widgets = {
            'text': forms.Textarea()
        }


class NewClubForm(forms.ModelForm):
    """Form for creating a new book club."""

    class Meta:
        model = Club
        fields = [
            'name',
            'description',
            'avg_reading_speed',
            'meeting_type',
        ]

    city = forms.CharField(
        label="City",
        max_length=250
    )

    country = CountryField(blank_label='(Select country)').formfield()

    calendar_name = forms.CharField(
        label='Calendar name',
        widget=forms.Textarea(
            attrs={'placeholder': "It's a good idea to make it simple: easy to say and easy to remember."}
        )
    )

    def clean(self):
        """ Ensure that calendar name is unique."""

        super().clean()
        calendar_name = self.cleaned_data.get('calendar_name')
        calendar_slug = slugify(calendar_name)
        calendar_with_same_name = Calendar.objects.filter(slug=calendar_slug)
        if calendar_with_same_name.exists():
            self.add_error('calendar_name',
                           'Calendar name is already taken.')


class MeetingAddressForm(forms.ModelForm):
    class Meta:
        model = MeetingAddress
        fields = ['address']


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['name', 'address1', 'address2', 'zip_code', 'city']

    country = CountryField(blank_label='(Select country)').formfield()


class MeetingLinkForm(forms.ModelForm):
    class Meta:
        model = MeetingLink
        fields = ['meeting_link']


class CreateEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'start', 'end', 'end_recurring_period', 'rule']

    start = forms.SplitDateTimeField(
        widget=forms.SplitDateTimeWidget(),
        initial=datetime.datetime.now
    )

    default_meeting_start = datetime.datetime.now()
    default_meeting_lenth_in_hours = 1
    default_meeting_lenth_delta = datetime.timedelta(hours=default_meeting_lenth_in_hours)
    meeting_end = default_meeting_start + default_meeting_lenth_delta
    end = forms.SplitDateTimeField(
        widget=forms.SplitDateTimeWidget(),
        initial=meeting_end)

    # end_recurring_period = forms.DateTimeField(help_text=_("This date is ignored for one time only events."), required=False)

    end_recurring_period = forms.SplitDateTimeField(
        widget=forms.SplitDateTimeWidget(),
        initial=datetime.datetime.now,
        help_text=_("This date is ignored for one time only events."),
        required=False
    )

    def clean(self):
        super().clean()
        if self.cleaned_data['end'] <= self.cleaned_data['start']:
            self.add_error('end', 'The end time must be later than start time.')


class CalendarPickerForm(forms.Form):
    calendar = forms.ModelChoiceField(queryset=Calendar.objects.all().order_by('name'))
