from clubs.models import Address, User
from django.core.exceptions import ValidationError
from django.test import TestCase


class AddressTest(TestCase):

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self.address = Address(
            name="City Library",
            address1="New Concordia Wharf",
            address2="3 Mill St",
            zip_code="SE1 2BB",
            city="London",
            country="GB"
        )

    def test_valid_address(self):
        self._assert_address_is_valid()

    def test_name_must_not_be_blank(self):
        self.address.name = None
        self._assert_address_is_invalid()

    def test_name_must_not_be_overlong(self):
        self.address.name = 'x' + 'x' * 1024
        self._assert_address_is_invalid()

    def test_address1_must_not_be_blank(self):
        self.address.address1 = ''
        self._assert_address_is_invalid()

    def test_address1_must_not_be_overlong(self):
        self.address.address1 = 'x' + 'x' * 1024
        self._assert_address_is_invalid()

    def test_address2_may_be_blank(self):
        self.address.address2 = ''
        self._assert_address_is_valid()

    def test_zip_code_must_not_be_overlong(self):
        self.address.zip_code = 'x' + 'x' * 1024
        self._assert_address_is_invalid()

    def test_zip_code_may_be_blank(self):
        self.address.zip_code = ''
        self._assert_address_is_valid()

    def test_zip_code_must_not_be_overlong(self):
        self.address.zip_code = 'x' + 'x' * 12
        self._assert_address_is_invalid()

    def test_city_must_not_be_blank(self):
        self.address.city = ''
        self._assert_address_is_invalid()

    def test_city_must_not_be_overlong(self):
        self.address.city = 'x' + 'x' * 1024
        self._assert_address_is_invalid()

    def test_country_must_not_be_blank(self):
        self.address.country = ''
        self._assert_address_is_invalid()

    def test_country_must_not_be_overlong(self):
        self.address.country = 'x' + 'x' * 1024
        self._assert_address_is_invalid()

    def test_full_name_returns_collated_address_data(self):
        self.assertEqual(self.address.full_address(), f'{self.address.name}. {self.address.zip_code}, {self.address.address1}, {self.address.address2}. {self.address.city}, {self.address.country}.')

    def _assert_address_is_valid(self):
        try:
            self.address.full_clean()
        except (ValidationError):
            self.fail('Test address should be valid')

    def _assert_address_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.address.full_clean()
