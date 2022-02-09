import csv
from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from clubs.models import Club, User, Book, Club_Users, Club_Books, User_Books
import pandas as pd
import random
from random import randint
import uuid


class Command(BaseCommand):

    HOW_MANY_CLUBS_TO_MAKE = 5
    HOW_MANY_USERS_TO_ADD = 10
    HOW_MANY_BOOKS_TO_ADD = 50
    USER_ID = 0
    first_name = ""
    last_name = ""

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
        columns = ["ISBN", "Book_Title", "Book_Author", "Year_Of_Publication", "Publisher", "Image_URL_S", "Image_URL_M", "Image_URL_L"]
        book_data = pd.read_csv(
            r'clubs/dataset/BX-Books.csv',
            encoding='Latin-1',
            delimiter=';',
            names=columns,
            dtype={
                "ISBN": "string",
                "Book_Title": "string",
                "Book_Author": "string",
                "Year_Of_Publication" : "string",
                "Publisher" : "string",
                "Image_URL_S" : "string",
                "Image_URL_M" : "string",
                "Image_URL_L" : "string",
            }
        )
        return book_data   

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

        self.file1_append = open("seededClubs.txt", "a")
        self.file2_append = open("seededUsers.txt", "a")
        self.file3_append = open("seededBooks.txt", "a")

        self.clubs_made = []
        self.club_count = 0
        self.users_made = []
        self.user_count = 0
        self.books_made = []
        self.book_count = 0

        self.books_from_file = self.read_books_from_file()
        self.users_from_file = self.read_users_from_file()

    def __del__(self):
        self.file1_append.close()
        self.file2_append.close()
        self.file3_append.close()


    # took some code from our old seed.py file from grasshopper
    def create_club(self):
        # Initialise a user that will be the owner
        user = random.choice(User.objects.all())

        # Generate a club name based on a random owner name
        club_name = user.first_name + user.last_name + "\'s Club"

        # Append the new club name to the file
        self.file1_append.write(club_name + "\n")

        # If the club name doesn't already exist
        if not Club.objects.filter(name=club_name).exists():
            # Generate random club fields
            club_location = self.get_random_location()
            club_description = self.faker.text(max_nb_chars=520)
            club_reading_speed = random.randint(50, 500)

            # Create the club
            club = Club.objects.create(
                name=club_name,
                location=club_location,
                description=club_description,
                avg_reading_speed=club_reading_speed,
                owner=user
            )
            club.save()

            self.clubs_made.append(club)
            self.club_count += 1

            # Assigning favourite books to club
            fav_books = random.choices(Book.objects.all(), k = 5)
            for book in fav_books:
                fav_book = Club_Books.objects.create(
                    club = club,
                    book = book
                )
                fav_book.save()

    # seed users and add to clubs
    def seed_user_in_club(self):

            user = random.choice(User.objects.all())

            # Assigning favourite books to user
            fav_books = random.choices(Book.objects.all(), k = 5)
            for book in fav_books:
                fav_book = User_Books.objects.create(
                    user = user,
                    book = book
                )
                fav_book.save()
        
            # Add the new user to a random club
            random_int = randint(0, (len(self.clubs_made) - 1))
            club_choice = self.clubs_made[random_int]

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
                    id = user_id,
                    first_name = user_first_name,
                    last_name = user_last_name,
                    email = str(user_first_name) + "." + str(user_last_name) + str(user_id) + "@example.com",
                    username = '@' + str(user_first_name) + str(user_last_name) + str(user_id),
                    password = 'Password123',
                    bio = self.faker.text(max_nb_chars=520)
                )
                user.save() 
               
                # Append the new user id to the file
                self.file2_append.write(user.id + "\n")
                self.users_made.append(user)
                self.user_count += 1        


    def seed_book_from_csv(self): 
            
            rand_choice = self.get_random_book()

            if not Book.objects.filter(ISBN=self.books_from_file['ISBN'][rand_choice]).exists():   
                book = Book.objects.create(
                    ISBN = self.books_from_file['ISBN'][rand_choice],
                    title = self.books_from_file['Book_Title'][rand_choice],
                    author = self.books_from_file['Book_Author'][rand_choice],
                    publication_year = self.books_from_file['Year_Of_Publication'][rand_choice],
                    publisher = self.books_from_file['Publisher'][rand_choice]
                    )
                book.save() 
               
                # Append the new book ISBN to the file
                self.file3_append.write(book.ISBN + "\n")
                self.books_made.append(book)
                self.book_count += 1


    # get a random index from the list of books in the dataset
    def get_random_book(self):
        return random.choice(self.books_from_file.index)


    # generate a random location from a made-up list (can also do it with the user locations but we would have to format them first)
    def get_random_location(self):
        locations = ["London", "Manchester", "Birmingham",
                     "Brighton", "Bristol", "Online", "Glasgow", "USA"]
        return random.choice(locations)

    # get a random index from the list of users in the dataset
    def get_random_user(self):
        return random.choice(self.users_from_file.index)


    def handle(self, *args, **options):

        book_count = 1
        while self.book_count < self.HOW_MANY_BOOKS_TO_ADD:
            print(f'Seeding book {book_count}',  end='\r')
            self.seed_book_from_csv()
            book_count += 1
        print('Finished seeding books')   
        
        user_count = 1
        while self.user_count < self.HOW_MANY_USERS_TO_ADD:
            print(f'Seeding user {user_count}',  end='\r')
            self.seed_user_from_csv()
            user_count += 1
        print('Finished seeding users') 
        self.user_count = 0

        club_count = 1
        while self.club_count < self.HOW_MANY_CLUBS_TO_MAKE:
            print(f'Seeding club {club_count}',  end='\r')
            self.create_club()
            club_count += 1
        print('Finished seeding clubs')

        user_count = 1
        while self.user_count < self.HOW_MANY_USERS_TO_ADD:
            print(f'Adding user {user_count}',  end='\r')
            self.seed_user_in_club()
            user_count += 1
        print('Finished adding users to clubs')