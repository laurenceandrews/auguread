from pickle import FALSE

from django.db import models
from django_countries.fields import CountryField
from schedule.models import Calendar, Event, Rule


class MeetingLink(models.Model):
    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE
    )

    meeting_link = models.URLField(
        blank=False
    )

    class Meta:
        app_label = "clubs"
        verbose_name = "Meeting Link"
        verbose_name_plural = "Meeting Links"


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

    class Meta:
        app_label = "clubs"
        verbose_name = "Address"
        verbose_name_plural = "Addresses"

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
        app_label = "clubs"
        verbose_name = "Meeting Address"
        verbose_name_plural = "Meeting Addresses"
