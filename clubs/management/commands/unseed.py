from clubs.models import (Address, Book, Book_Rating, Club, Club_Book_History,
                          Club_Books, Club_Users, MeetingAddress, MeetingLink,
                          Post, User, User_Book_History, User_Books)
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
        print("Successfully deleted all posts.")

        Club.objects.all().delete()
        print("Successfully deleted all clubs.")

        Club_Users.objects.all().delete()
        print("Successfully deleted all club users.")

        Calendar.objects.all().delete()
        Event.objects.all().delete()
        Rule.objects.all().delete()
        print("Successfully deleted all calendars, events and rules.")

        Address.objects.all().delete()
        MeetingLink.objects.all().delete()
        MeetingAddress.objects.all().delete()
        print("Successfully deleted all address, meeting link and meeting address objects.")

        Book.objects.all().delete()
        print("Successfully deleted all books.")

        Book_Rating.objects.all().delete()
        print("Successfully deleted all book ratings.")

        Club_Book_History.objects.all().delete()
        Club_Books.objects.all().delete()
        print("Successfully deleted all club book histories and favourites.")

        User_Book_History.objects.all().delete()
        User_Books.objects.all().delete()
        print("Successfully deleted all user book histories and favourites.")
