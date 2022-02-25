from clubs.models import Club, Post, User
from django.core.management.base import BaseCommand, CommandError
from schedule.models import Calendar, Event, Rule


class Command(BaseCommand):
    help = 'Seeds the database with sample data'

    def handle(self, *args, **options):
        non_admin_users = User.objects.filter(is_staff=False)
        for i in non_admin_users:
            i.delete()
        print("Successfully deleted all non-admin users.")

        Post.objects.all().delete()

        Club.objects.all().delete()
        print("Successfully deleted all clubs.")

        Calendar.objects.all().delete()
        Event.objects.all().delete()
        Rule.objects.all().delete()
        print("Successfully deleted all calendars, events and rules.")
