"""Unit tests for the User model."""
from django.test import TestCase
from clubs.models import User, Club


class UserModelTestCase(TestCase):
    """Unit tests for the User model."""

    fixtures = [
        'clubs/tests/fixtures/club.json',
        'clubs/tests/fixtures/owner_user.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.owner_user = self.club.owner
        self.member_user = Club.objects.get(id=1).members.all()[0]
        self.owner_user = Club.objects.get(id=1).owner.all()[0]
        self.applicant_user = Club.objects.get(id=1).applicants.all()[0]
        self.user = User.objects.get(id=2)

    def test_is_applicant(self):
        self.assertTrue(self.applicant_user.is_applicant(self.club))

    def test_is_owner(self):
        self.assertTrue(self.owner_user.is_owner(self.club))

    def test_is_officer(self):
        self.assertTrue(self.owner_user.is_owner(self.club))

    def test_member_membership_type(self):
        self.assertEqual(self.member_user.membership_type(self.club), 'Member')

    def test_applicant_membership_type(self):
        self.assertEqual(self.applicant_user.membership_type(
            self.club), 'Applicant')

    def test_user_membership_type(self):
        self.assertEqual(self.user.membership_type(self.club), 'User')

    def test_demote_officer(self):
        self.club.toggle_promote(self.owner_user)
        self.assertTrue(self.owner_user in self.club.members.all())

    def test_promote_member(self):
        self.club.toggle_promote(self.member_user)
        self.assertTrue(self.member_user in self.club.owners.all())

    def test_transfer(self):
        self.club.transfer(self.owner_user)
        self.assertEqual(self.club.owner, self.owner_user)

    def test_can_not_transfer_to_member(self):
        self.club.transfer(self.member_user)
        self.assertNotEqual(self.club.owner, self.officer_user)

    def test_in_club(self):
        self.assertTrue(self.club.in_club(self.owner_user))
        self.assertTrue(self.club.in_club(self.applicant_user))
        self.assertTrue(self.club.in_club(self.applicant_user))
        self.assertFalse(self.club.in_club(self.user))
