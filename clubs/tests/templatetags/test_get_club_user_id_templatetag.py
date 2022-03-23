from clubs.models import Club, Club_Users, User
from clubs.templatetags.get_club_user_id import get_club_user_id
from django.test import TestCase


class ClubUserRoleNumTemplatetagTestCase(TestCase):

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_calendar.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_clubs.json',
        'clubs/tests/fixtures/default_rules.json'
    ]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.club = Club.objects.get(pk=6)
        self.club_user = Club_Users.objects.get(user=self.user, club=self.club)

    def test_valid_input_with_existing_club_user(self):
        result = get_club_user_id(self.club, self.user)
        self.assertEqual(result, self.club_user.id)

    def test_valid_input_with_no_existing_club_user(self):
        user = User.objects.get(pk=2)
        result = get_club_user_id(self.club, user)
        self.assertEqual(result, None)
