from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from clubs.models import Club, User, Club_Users, Club_Books
import pandas as pd
import random
from random import randint


class Command(BaseCommand):

    HOW_MANY_CLUBS_TO_MAKE = 10
    HOW_MANY_USERS_TO_ADD = 100
    USER_ID = 0
    first_name = ""
    last_name = ""

    # get users from the database separated into columns (using pandas)
    def read_from_file(self):
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

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

        self.file1_append = open("seededClubs.txt", "a")
        self.file2_append = open("seededUsers.txt", "a")

        self.clubs_made = []
        self.club_count = 0
        self.users_made = []
        self.user_count = 0

    def __del__(self):
        self.file1_append.close()
        self.file2_append.close()

    # took some code from our old seed.py file from grasshopper
    def create_club(self):
        # Initialise a user that will be the owner
        owner_first_name = self.faker.first_name()
        owner_last_name = self.faker.last_name()
        emailTuple = str(owner_first_name) + "." + str(owner_last_name) + "@example.com"
        owner_username = '@' + str(owner_first_name)
        owner_password = 'Password123'
        owner_bio = self.faker.text(max_nb_chars=520)

        # Generate a club name based on a random owner name
        club_name = owner_first_name + owner_last_name + "\'s Club"

        # Append the new club name to the file
        self.file1_append.write(club_name + "\n")

        # If the club name doesn't already exist
        if not Club.objects.filter(name=club_name).exists():
            # Generate random club fields
            club_location = self.generate_random_location()
            club_description = self.faker.text(max_nb_chars=520)
            club_reading_speed = random.randint(50, 500)
            
            # Get random id
            ownerId = self.get_random_user()
            
            # If a user with the above id isn't already seeded
            if not User.objects.filter(id=ownerId).exists():
                # Seed that user. This will be the owner
                user = User.objects.create_user(
                    id = ownerId,
                    first_name = owner_first_name,
                    last_name = owner_last_name,
                    email = ''.join(emailTuple),
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

    # get a random user id from the list of users in the dataset
    def get_random_user(self):
        ids = self.read_from_file().id.to_list()
        random.choice(ids)

    # generate a random location from a made-up list (can also do it with the user locations but we would have to format them first)
    def generate_random_location(self):
        locations = ["London", "Manchester", "Birmingham",
                     "Brighton", "Bristol", "Online", "Glasgow", "USA"]
        return random.choice(locations)

    def seed_user_in_club(self):
        user_first_name = self.faker.first_name()
        user_last_name = self.faker.last_name()
        emailTuple = str(user_first_name) + "." + str(user_last_name) + "@example.com"
        user_username = '@' + str(user_first_name)
        user_password = 'Password123'
        user_bio = self.faker.text(max_nb_chars=520)

        # Seed a user using existing and randomly generated data
        if not User.objects.filter(username=user_username).exists():
            user = User.objects.create_user(
                id = self.user_count,
                first_name = user_first_name,
                last_name = user_last_name,
                email = ''.join(emailTuple),
                username = user_username,
                password = user_password,
                bio = self.faker.text(max_nb_chars=520)
            )
            user.save()
    
            # Add the new user to a random club
            random_int = randint(0, (len(self.clubs_made) - 1))
            club_choice = self.clubs_made[random_int]

            # Set user role in club
            user_role = Club_Users.objects.create(
                user_id=user,
                club_id=club_choice,
                role_num=randint(1, 3)
            )
            user_role.save()

            self.user_count += 1

    def handle(self, *args, **options):
        while self.club_count < self.HOW_MANY_CLUBS_TO_MAKE:
            print(f'Seeding clubs...',  end='\r')
            self.create_club()
            self.club_count += 1
        print('Finished seeding clubs')

        while self.user_count < self.HOW_MANY_USERS_TO_ADD:
            print(f'Adding users to clubs...',  end='\r')
            self.seed_user_in_club()
            self.user_count += 1
        print('Finished adding users to clubs')