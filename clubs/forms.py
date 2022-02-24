"""Forms for the book club app"""


from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from django_countries.fields import CountryField

from schedule.models import Calendar, Event, Rule


from django.utils.translation import ugettext_lazy as _

from .models import Club, Post, User


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
        fields = ['name', 'location', 'description']

    calendar_name = forms.CharField(
        label='Calendar name',
        widget=forms.Textarea(
            attrs={'placeholder': "It's a good idea to make it simple: easy to say and easy to remember."}
        )
    )


class CalendarPickerForm(forms.Form):
    calendar = forms.ModelChoiceField(queryset=Calendar.objects.all().order_by('name'))
