from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from clubs.models import User, Book

class Command(BaseCommand):
    PASSWORD = "Password123"
    USER_COUNT = 100
    BOOK_COUNT = 100

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        user_count = 0
        while user_count < Command.USER_COUNT:
            print(f'Seeding user {user_count}',  end='\r')
            try:
                self._create_user()
            except (django.db.utils.IntegrityError):
                continue
            user_count += 1
        print('User seeding complete')

    def handle(self, *args, **options):
        book_count = 0
        while book_count < Command.BOOK_COUNT:
            print(f'Seeding book {book_count}',  end='\r')
            try:
                self._create_book()
            except (django.db.utils.IntegrityError):
             continue
            book_count += 1
        print('Book seeding complete') 

    def _create_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = self._email(first_name, last_name)
        username = self._username(first_name, last_name)
        bio = self.faker.text(max_nb_chars=520)
        User.objects.create_user(
            username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=Command.PASSWORD,
            bio=bio
        )

    def _email(self, first_name, last_name):
        email = f'{first_name}.{last_name}@example.org'
        return email

    def _username(self, first_name, last_name):
        username = f'@{first_name}{last_name}'
        return username

    def _create_book(self):
        ISBN = self.faker.isbn13()
        title = self.faker.text(max_nb_chars=20)
        author = self.faker.name()
        publisher = self.faker.company()
        publication_year = self.faker.year()
        Book.objects.create(
            ISBN = ISBN,
            title = title,
            author = author,
            publisher = publisher,
            publication_year = publication_year
        )