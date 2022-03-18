import csv
import datetime
import random
import time
from random import randint

import pandas as pd
from clubs.models import (Book, Book_Rating, Club, Club_Books, Club_Users,
                          User, User_Books)
from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify
from faker import Faker
from schedule.models import Calendar, Event, Rule


class Command(BaseCommand):

    HOW_MANY_CLUBS_TO_ADD = 10
    HOW_MANY_USERS_TO_ADD = 500
    HOW_MANY_BOOKS_TO_ADD = 500
    HOW_MANY_RATINGS_TO_ADD = 500
    USER_ID = 0
    first_name = ""
    last_name = ""

    def set_users(self):
        self.users = User.objects.all()

    def set_books(self):
        self.books = Book.objects.all()

    def set_clubs(self):
        self.clubs = Club.objects.all()

    # get users from the database separated into columns (using pandas)

    def read_users_from_file(self):
        columns = ["id", "Location", "Age"]
        user_data = pd.read_csv(
            r'clubs/dataset/BX-Users.csv',
            encoding='Latin-1',
            delimiter=';',
            names=columns,
            dtype={
                "id": "string",
                "Location": "string",
                "Age": "string",
            }
        )
        return user_data

    # get books from the database separated into columns (using pandas)
    def read_books_from_file(self):
        columns = ["ISBN", "Book_Title", "Book_Author", "Year_Of_Publication",
                   "Publisher", "Image_URL_S", "Image_URL_M", "Image_URL_L"]
        book_data = pd.read_csv(
            r'clubs/dataset/BX-Books.csv',
            encoding='Latin-1',
            delimiter=';',
            names=columns,
            dtype={
                "ISBN": "string",
                "Book_Title": "string",
                "Book_Author": "string",
                "Year_Of_Publication": "string",
                "Publisher": "string",
                "Image_URL_S": "string",
                "Image_URL_M": "string",
                "Image_URL_L": "string",
            }
        )
        return book_data

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

        self.file1_append = open("seededClubs.txt", "a")
        self.file2_append = open("seededUsers.txt", "a")
        self.file3_append = open("seededBooks.txt", "a")

        self.club_count = 0
        self.user_count = 0
        self.book_count = 0
        self.rating_count = 0

        # Holds all users books and clubs to be used as a cache for when seeded
        self.users = []
        self.books = []
        self.clubs = []

        # To update display when seeding
        self.books_seeded = 1
        self.users_seeded = 1
        self.clubs_seeded = 1
        self.ratings_seeded = 1

        self.books_from_file = self.read_books_from_file()
        self.users_from_file = self.read_users_from_file()

    def __del__(self):
        self.file1_append.close()
        self.file2_append.close()
        self.file3_append.close()

    # create rules for calendars
    rule = Rule(frequency="YEARLY", name="Yearly",
                description="will recur once every Year")
    rule.save()
    print("YEARLY recurrence created")
    rule = Rule(frequency="MONTHLY", name="Monthly",
                description="will recur once every Month")
    rule.save()
    print("Monthly recurrence created")
    rule = Rule(frequency="WEEKLY", name="Weekly",
                description="will recur once every Week")
    rule.save()
    print("Weekly recurrence created")
    rule = Rule(frequency="DAILY", name="Daily",
                description="will recur once every Day")
    rule.save()
    print("Daily recurrence created")

    # took some code from our old seed.py file from grasshopper
    def create_club(self):
        # Initialise a user that will be the owner
        user = random.choice(self.users)

        # Generate a club name based on a random owner name
        club_name = user.first_name + " " + user.last_name + "\'s Club"

        # Append the new club name to the file
        self.file1_append.write(club_name + "\n")

        # If the club name doesn't already exist
        if not Club.objects.filter(name=club_name).exists():
            # Generate random club fields
            club_location = self.get_random_location()
            club_description = self.faker.text(max_nb_chars=520)
            club_reading_speed = random.randint(50, 500)

            calendar_name = club_name + "\'s Calendar"
            calendar_slug = slugify(calendar_name)
            cal = Calendar(name=calendar_name, slug=calendar_slug)
            cal.save()

            # Create the club
            club = Club.objects.create(
                name=club_name,
                location=club_location,
                description=club_description,
                avg_reading_speed=club_reading_speed,
                owner=user,
                calendar=cal
            )
            club.save()

            # self.clubs_made.append(club)
            self.club_count += 1
            self.clubs_seeded += 1

            # Assigning favourite books to club
            fav_books = random.choices(self.books, k=5)
            for book in fav_books:
                fav_book = Club_Books.objects.create(
                    club=club,
                    book=book
                )
                fav_book.save()

    # seed users and add to clubs
    def seed_user_in_club(self):

        user = random.choice(self.users)

        # Assigning favourite books to user
        fav_books = random.choices(self.books, k=5)
        for book in fav_books:
            fav_book = User_Books.objects.create(
                user=user,
                book=book
            )
            fav_book.save()

        # Add the new user to a random club
        club_choice = random.choice(self.clubs)

        # Ensures that the user isn't made a member of a club that they own
        while(club_choice.owner.id == user.id):
            club_choice = random.choice(self.clubs)

        # Set user role in club
        user_role = Club_Users.objects.create(
            user=user,
            club=club_choice,
            role_num=randint(1, 3)
        )
        user_role.save()

        self.user_count += 1

    def seed_user_from_csv(self):

        rand_choice = self.get_random_user()

        user_id = self.users_from_file['id'][rand_choice]
        user_first_name = self.faker.first_name()
        user_last_name = self.faker.last_name()

        if not User.objects.filter(id=user_id).exists():
            user = User.objects.create(
                id=int(user_id),
                first_name=user_first_name,
                last_name=user_last_name,
                email=str(user_first_name) + "." +
                str(user_last_name) + str(user_id) + "@example.com",
                username='@' + str(user_first_name) +
                str(user_last_name) + str(user_id),
                password='Password123',
                age=random.randint(1, 150),
                bio=self.faker.text(max_nb_chars=10),
                country=self.users_from_file['Location'][rand_choice]
            )
            user.save()

            # Append the new user id to the file
            self.file2_append.write(str(user.id) + "\n")
            # self.users_made.append(user)
            self.user_count += 1
            self.users_seeded += 1

    def seed_book_from_csv(self):

        rand_choice = self.get_random_book()

        if not Book.objects.filter(ISBN=self.books_from_file['ISBN'][rand_choice]).exists():
            book = Book.objects.create(
                ISBN=self.books_from_file['ISBN'][rand_choice],
                title=self.books_from_file['Book_Title'][rand_choice],
                author=self.books_from_file['Book_Author'][rand_choice],
                publication_year=self.books_from_file['Year_Of_Publication'][rand_choice],
                publisher=self.books_from_file['Publisher'][rand_choice],
                image_small=self.books_from_file['Image_URL_S'][rand_choice],
                image_medium=self.books_from_file['Image_URL_M'][rand_choice],
                image_large=self.books_from_file['Image_URL_L'][rand_choice],
            )
            book.save()

            # Append the new book ISBN to the file
            self.file3_append.write(book.ISBN + "\n")
            # self.books_made.append(book)
            self.book_count += 1
            self.books_seeded += 1

    def seed_ratings(self):

        user = random.choice(self.users)
        book = random.choice(self.books)

        if not Book_Rating.objects.filter(user=user, book=book).exists():

            book_rating = Book_Rating.objects.create(
                user=user,
                book=book,
                rating=randint(1, 10)
            )

            book_rating.save()
            self.rating_count += 1
            self.ratings_seeded += 1

    # get a random index from the list of books in the dataset
    def get_random_book(self):
        return random.choice(self.books_from_file.index)

    # generate a random city and country from a made-up list (can also do it with the user locations but we would have to format them first)
    def get_random_location(self):
        city = [
            "London, UK", "Manchester, UK,", "Birmingham, UK", "Brighton, UK", "Bristol, UK",
            "Berlin, Germany", "Hamburg, Germany", "Munich, Germany", "Cologne, Germany", "Frankfurt, Germany",
            "Mumbai, India", "Delhi, India", "Bangalore, India", "Kolkata, India", "Chennai, India",
            "Sydney, Australia", "Melbourn, Australia", "Brisbane, Australia", "Perth, Australia", "Adelaide, Australia",
            "Toronto, Canada", "Montreal, Canada", "Calgary, Canada", "Ottawa, Canada", "Edmonton, Canada",
            "Rio de Janeiro, Brazil", "Sao Paulo, Brazil", "Belo Horizonte, Brazil", "Salvador, Brazil", "Manaus, Brazil",
            "Tokyo, Japan", "Yokohama, Japan", "Osaka, Japan", "Nagoya, Japan", "Sapporo, Japan",
            "Lagos, Nigeria", "Kano, Nigeria", "Ibadan, Nigeria", "Kaduna, Nigeria", "Port Harcourt, Nigeria",
            "Cairo, Egypt", "Aswan, Egypt", "Luxor, Egypt", "Alexandria, Egypt", "Sharm El Sheikh, Egypt"
        ]
        return random.choice(city)

    # get a random index from the list of users in the dataset
    def get_random_user(self):
        return random.choice(self.users_from_file.index)

    def handle(self, *args, **options):
        start = time.time()
        while self.book_count < self.HOW_MANY_BOOKS_TO_ADD:
            print(f'Seeding book {self.books_seeded}',  end='\r')
            self.seed_book_from_csv()
        print('Finished seeding books')
        end = time.time()
        print(f'Time to seed books: {end - start}')

        self.set_books()

        start = time.time()
        while self.user_count < self.HOW_MANY_USERS_TO_ADD:
            print(f'Seeding user {self.users_seeded}',  end='\r')
            self.seed_user_from_csv()
        print('Finished seeding users')
        end = time.time()
        print(f'Time to seed users: {end - start}')
        self.user_count = 0

        self.set_users()

        start = time.time()
        while self.club_count < self.HOW_MANY_CLUBS_TO_ADD:
            print(f'Seeding club {self.clubs_seeded}',  end='\r')
            self.create_club()
            self.clubs_seeded += 1
        print('Finished seeding clubs')
        end = time.time()
        print(f'Time to seed clubs: {end - start}')

        self.set_clubs()

        start = time.time()
        while self.rating_count < self.HOW_MANY_RATINGS_TO_ADD:
            print(f'Seeding rating {self.ratings_seeded}',  end='\r')
            self.seed_ratings()
        print('Finished seeding ratings')
        end = time.time()
        print(f'Time to seed ratings: {end - start}')

        start = time.time()
        self.users_seeded = 1
        while self.user_count < self.HOW_MANY_USERS_TO_ADD:
            print(f'Adding user {self.users_seeded}',  end='\r')
            self.seed_user_in_club()
            self.users_seeded += 1
        print('Finished adding users to clubs')
        end = time.time()
        print(f'Time to add users to clubs: {end - start}')
