from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from clubs.models import Club, User, Club_Users, Club_Books
import pandas as pd
import random
from random import randint


class Command(BaseCommand):

    HOW_MANY_CLUBS_TO_MAKE = 10
    HOW_MANY_USERS_TO_ADD = 100

    # get users from the database separated into columns (using pandas)
    def read_from_file(self):
        columns = ["UserID", "Location", "Age"]
        user_data = pd.read_csv(
            r'clubs/dataset/BX-Users.csv', encoding='Latin-1', delimiter=';', names=columns)
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
        # Generate a club name based on a random owner name
        owner_first_name = self.faker.first_name()
        owner_last_name = self.faker.last_name()
        club_name = owner_first_name + owner_last_name + "\'s Club"
        # Append the new club name to the file
        self.file1_append.write(club_name + "\n")

        # If the club name doesn't already exist
        if not Club.objects.filter(name=club_name).exists():
            # Generate random club fields
            club_location = self.generate_random_location()
            club_description = self.faker.text(max_nb_chars=520)
            club_reading_speed = random.randint(50, 500)
            
            # Get random userId
            userId = self.get_random_user(),
            
            # If a user with the above userId isn't already seeded
            if not User.objects.filter(userId=userId).exists():
                # Seed that user. This will be the owner
                user = User.objects.create_user(
                    userId = userId,
                    first_name = owner_first_name,
                    last_name = owner_last_name,
                    email = self.first_name.lower() + '.' + self.last_name.lower() + '@example.org',  
                    emailTuple = str(self.first_name) + "." + str(self.last_name) + "@example.com",
                    password='Password123',
                    bio = self.faker.text(max_nb_chars=520)
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
        user_ids = self.read_from_file().UserID.to_list()
        random.choice(user_ids)

    # generate a random location from a made-up list (can also do it with the user locations but we would have to format them first)
    def generate_random_location(self):
        locations = ["London", "Manchester", "Birmingham",
                     "Brighton", "Bristol", "Online", "Glasgow", "USA"]
        return random.choice(locations)

    
    def seed_user_in_club(self):
        # Seed a user using existing and randomly generated data
        user = User.objects.create_user(
            userId = self.user_count,
            first_name = self.faker.first_name(),
            last_name = self.faker.last_name(),
            email = self.first_name.lower() + '.' + self.last_name.lower() + '@example.org',  
            emailTuple = str(self.first_name) + "." + str(self.last_name) + "@example.com",
            password='Password123',
            bio = self.faker.text(max_nb_chars=520)
        )
        user.save()
    
        # Add the new user to a random club
        random_int = randint(0, (len(self.clubs_made) - 1))
        club_choice = self.clubs_made[random_int]

        # Set user role in club
        user_role = Club_Users.objects.create(
            user=user,
            club=club_choice,
            num=randint(1, 3)
        )
        user_role.save()

        self.how_many_users_made += 1

    def handle(self, *args, **options):
        while self.club_count < self.HOW_MANY_CLUBS_TO_MAKE:
            print(f'Seeding clubs...',  end='\r')
            self.create_club()
            self.club_count += 1
        print('Finished seeding clubs')

        while self.how_many_users_added < self.HOW_MANY_USERS_TO_ADD:
            print(f'Adding users to clubs...',  end='\r')
            self.seed_user_in_club()
            self.user_count += 1
        print('Finished adding users to clubs')