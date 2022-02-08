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
    HOW_MANY_BOOKS_TO_ADD = 5
    USER_ID = 0
    first_name = ""
    last_name = ""

    book_ISBN = []
    book_title = []
    book_author = []
    book_publication_year = []
    book_publisher = []
    books = [book_ISBN, book_title, book_author, book_publication_year, book_publisher]

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

    def __del__(self):
        self.file1_append.close()
        self.file2_append.close()
        self.file3_append.close()


    # took some code from our old seed.py file from grasshopper
    def create_club(self):
        # Initialise a user that will be the owner
        owner_id = self.get_random_user()
        owner_first_name = self.faker.first_name()
        owner_last_name = self.faker.last_name()
        email_tuple = str(owner_first_name) + "." + str(owner_last_name) + str(owner_id) + "@example.com"
        owner_username = '@' + str(owner_first_name) + str(owner_last_name) + str(owner_id)
        owner_password = 'Password123'
        owner_bio = self.faker.text(max_nb_chars=520)

        # Generate a club name based on a random owner name
        club_name = owner_first_name + owner_last_name + "\'s Club"

        # Append the new club name to the file
        self.file1_append.write(club_name + "\n")

        # If the club name doesn't already exist
        if not Club.objects.filter(name=club_name).exists():
            # Generate random club fields
            club_location = self.get_random_location()
            club_description = self.faker.text(max_nb_chars=520)
            club_reading_speed = random.randint(50, 500)
                        
            # If a user with the above id isn't already seeded
            if not User.objects.filter(id=owner_id).exists():
                # Seed that user. This will be the owner
                user = User.objects.create_user(
                    id = owner_id,
                    first_name = owner_first_name,
                    last_name = owner_last_name,
                    email = ''.join(email_tuple),
                    username = owner_username,
                    password = owner_password,
                    bio = owner_bio
                )
                user.save()

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
        user_id = self.get_random_user()
        user_first_name = self.faker.first_name()
        user_last_name = self.faker.last_name()
        email_tuple = str(user_first_name) + "." + str(user_last_name) + str(user_id) + "@example.com"
        user_username = '@' + str(user_first_name) + str(user_last_name) + str(user_id)
        user_password = 'Password123'
        user_bio = self.faker.text(max_nb_chars=520)

        # Seed a user using existing and randomly generated data
        if not User.objects.filter(id=user_id).exists():            
            user = User.objects.create_user(
                id = user_id,
                first_name = user_first_name,
                last_name = user_last_name,
                email = ''.join(email_tuple),
                username = user_username,
                password = user_password,
                bio = user_bio
            )
            user.save()

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

    def create_book(self):
        ISBN = self.faker.isbn13()
        book = Book.objects.create(
                ISBN = ISBN,
                title = self.faker.text(max_nb_chars=20),
                author = self.faker.name(),
                publication_year = self.faker.year(),
                publisher = self.faker.company()
            )
        book.save()

        # Append the new book name to the file
        self.file1_append.write(ISBN + "\n")

        self.books_made.append(book)
        self.book_count += 1

    def load_all_books(self):
        self.books[0] = self.read_books_from_file().ISBN.to_list()
        self.books[1] = self.read_books_from_file().Book_Title.to_list()
        self.books[2] = self.read_books_from_file().Book_Author.to_list()
        self.books[3] = self.read_books_from_file().Year_Of_Publication.to_list()
        self.books[4] = self.read_books_from_file().Publisher.to_list()

    def seed_book_from_csv(self):
        book = self.get_random_book()
        ISBN = book[0]

        # Seed a user using existing and randomly generated data
        if not Book.objects.filter(ISBN=ISBN).exists():   
            book = Book.objects.create(
                    ISBN = str(ISBN),
                    title = str(book[1]),
                    author = str(book[2]),
                    publication_year = str(book[3]),
                    publisher = str(book[4])
                )
            book.save()
        
        # Append the new book name to the file
        self.file1_append.write(ISBN + "\n")

        self.books_made.append(book)
        self.book_count += 1

    # get random ISBNs from the list of books in the dataset (currently chooses 5)
    def get_random_book(self):
        #self.read_books_from_file().sample()
        random.choice(self.books)

    # generate a random location from a made-up list (can also do it with the user locations but we would have to format them first)
    def get_random_location(self):
        locations = ["London", "Manchester", "Birmingham",
                     "Brighton", "Bristol", "Online", "Glasgow", "USA"]
        return random.choice(locations)

     # get a random user id from the list of users in the dataset
    def get_random_user(self):
        ids = self.read_users_from_file().id.to_list()
        random.choice(ids)

    def handle(self, *args, **options):

        print(f'Loading all books',  end='\r')
        self.load_all_books()

        book_count = 1
        while self.book_count < self.HOW_MANY_BOOKS_TO_ADD:
            print(f'Seeding book {book_count}',  end='\r')
            self.seed_book_from_csv()
            book_count += 1
        print('Finished seeding books')   
        
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