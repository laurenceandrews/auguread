from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from clubs.models import Club, User
import pandas as pd
import random


class Command(BaseCommand):

    CLUB_COUNT = 5
    club_count = 0

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

        self.clubs_made = []
        self.club_count = 0

    def __del__(self):
        self.file1_append.close()

    # the try catch gives an error so i left it out for now
    def handle(self, *args, **options):
        while self.club_count < self.CLUB_COUNT:
            print(f'Seeding clubs...',  end='\r')
            # try:
            self.create_club()
            # except (django.db.utils.IntegrityError):
            #     continue
            self.club_count += 1
        print('Club seeding complete')

    # took some code from our old seed.py file from grasshopper
    def create_club(self):
        club_name = self.faker.name() + "\'s club"
        self.file1_append.write(club_name + "\n")

        if not Club.objects.filter(name=club_name).exists():
            club_description = self.faker.text(max_nb_chars=520)
            location = self.generate_random_location()
            reading_speed = random.randint(50, 500)
            userId = self.get_random_user()
            first_name = self.faker.first_name(),
            last_name = self.faker.last_name(),
            emailTuple = str(first_name) + "." + str(last_name) + "@example.com",
            email = ''.join(emailTuple)
            username = '@' + str(first_name),
            bio = self.faker.text(max_nb_chars=520)

            # create a user to be the owner of the club
            if not User.objects.filter(id=userId).exists():
                user = User.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    email=email,
                    bio=bio
                )
                user.save()

            # create the club
            club = Club.objects.create(
                name=club_name,
                location=self.faker.address(),
                description=club_description,
                avg_reading_speed=reading_speed,
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
