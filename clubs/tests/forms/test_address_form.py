"""Unit tests of the address form."""
from clubs.forms import AddressForm
from django.test import TestCase


class MeetingLinkFormTestCase(TestCase):
    """Unit tests of the meeting address form."""

    def setUp(self):
        self.form_input = {
            "name": "City Library",
            "address1": "New Concordia Wharf",
            "address2": "3 Mill St",
            "zip_code": "SE1 2BB",
            "city": "London",
            "country": "GB"
        }

    def test_valid_address_form(self):
        form = AddressForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = AddressForm()
        self.assertIn('name', form.fields)
        self.assertIn('address1', form.fields)
        self.assertIn('address2', form.fields)
        self.assertIn('zip_code', form.fields)
        self.assertIn('city', form.fields)
        self.assertIn('country', form.fields)
