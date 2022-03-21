"""Unit tests for the User model."""
from clubs.models import Club, Club_Users, User
from django.test import TestCase


class ClubModelTestCase(TestCase):
    """Unit tests for the Club model."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/default_rules.json',
    ]

    def setUp(self):
        self.user = User.objects.get(pk=4)
        self.club = Club.objects.get(pk=6)
        self._create_club_owner_members_and_applicants()

    def test_is_applicant(self):
        self.assertTrue(self.applicant.is_applicant(self.club))

    def test_is_owner(self):
        self.assertTrue(self.owner.is_owner(self.club))

    def test_member_membership_type(self):
        self.assertEqual(self.member.membership_type(self.club), 'Member')

    def test_applicant_membership_type(self):
        self.assertEqual(self.applicant.membership_type(
            self.club), 'Applicant')

    # def test_officer_membership_type(self):
    #     self.assertEqual(self.officer.membership_type(self.club), 'Officer')

    def test_owner_membership_type(self):
        self.assertEqual(self.owner.membership_type(self.club), 'Owner')

    def test_transfer(self):
        self.club.transfer(self.member)
        self.assertEqual(self.club.owner, self.member)

    def test_can_not_transfer_to_applicant(self):
        self.club.transfer(self.applicant)
        self.assertNotEqual(self.club.owner, self.applicant)

    def test_in_club(self):
        self.assertTrue(self.club.in_club(self.owner))
        self.assertTrue(self.club.in_club(self.member))
        self.assertTrue(self.club.in_club(self.applicant))
        self.assertFalse(self.club.in_club(self.user))

    def _create_club_owner_members_and_applicants(self):
        self.owner = Club_Users.objects.get(club=self.club, role_num=4).user
        self.applicant = User.objects.get(pk=2)
        Club_Users.objects.create(user=self.applicant, club=self.club)
        self.member = User.objects.get(pk=3)
        Club_Users.objects.create(user=self.member, club=self.club, role_num=2)
