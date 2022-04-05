#!/usr/bin/env python
# coding: utf-8
# converted from a Jupyter notebook

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import scipy.sparse.linalg as spla
#from fuzzywuzzy import process, fuzz
from rapidfuzz import process, fuzz
from clubs.models import User, Club, Club_Users, Club_Books, Book, User_Books

pd.options.mode.chained_assignment = None  # default='warn'

class ClubUserRecommender:

    def __init__(self, user_id):
    # Load data
        self.book_df = pd.DataFrame(list(Book.objects.all().values()))
        self.user_df = pd.DataFrame(list(User.objects.all().values()))
        self.club_df = pd.DataFrame(list(Club.objects.all().values()))
        self.club_book_df = pd.DataFrame(list(Club_Books.objects.all().values()))
        self.club_user_df = pd.DataFrame(list(Club_Users.objects.all().values()))
        self.user_book_df = pd.DataFrame(list(User_Books.objects.all().values()))
        self.user_id = user_id

    # Declare global variables and DataFrames

        self.current_user = User.objects.get(pk=self.user_id)
        self.club_user_age_df = pd.DataFrame()
        self.club_user_location_df = pd.DataFrame()
        self.average_club_age_df = pd.DataFrame()
        self.average_club_age_difference_df = pd.DataFrame()
        self.closest_age_clubs_df = pd.DataFrame()
        self.club_user_count_df = pd.DataFrame()
        self.club_user_location_df = pd.DataFrame()
        self.club_favourite_books_df = pd.DataFrame()
        self.user_club_favourite_books_df = pd.DataFrame()
        self.my_favourite_books_df = pd.DataFrame()
        self.club_user_favourite_books_df = pd.DataFrame()
        self.club_user_title_matches_df = pd.DataFrame()
        self.club_average_book_match_df = pd.DataFrame()
        self.club_user_favourite_books_df_2 = pd.DataFrame()
        self.club_user_author_matches_df = pd.DataFrame()
        self.club_average_author_match_df = pd.DataFrame()
        self.best_clubs_df = pd.DataFrame()
        self.best_clubs_in_person_df = pd.DataFrame()
        self.best_clubs_online_df = pd.DataFrame()
        self.best_clubs_in_person_list = []
        self.best_clubs_online_list = []

        print("Loading recommendation system...")

        self.set_user()
        self.set_user_age_df()
        self.set_club_locations_df()
        self.set_average_club_age()
        self.set_age_difference_df()
        self.set_top_10_by_closest_age()
        self.set_user_count_per_club()
        self.set_clubs_with_matching_loc_fuzzy()
        self.set_club_favourite_books()
        self.set_user_club_favourite_books()
        self.set_fav_books_and_authors_per_user()
        self.set_club_user_favourite_books()
        self.set_club_user_favourite_books_df_2()
        self.set_all_favourite_book_matches_fuzzy()
        self.set_average_book_match_df()
        self.set_all_favourite_author_matches_fuzzy()
        self.set_club_average_author_match_df()
        self.set_best_clubs_df()
        self.set_best_clubs_in_person_df()
        self.set_best_clubs_online_df()
        self.set_best_clubs_in_person_list()
        self.set_best_clubs_online_list()

    # Sets the current user by getting the user id
    def set_user(self):
        current_user = User.objects.get(pk=self.user_id)
        self.current_user = current_user
    
    # Returns the current user
    def get_user(self):
        return self.current_user

    # Merge club_user junction table with user table to get ages of all users
    def set_user_age_df(self):
        club_user_age_df = self.club_user_df.merge(self.user_df, left_on = 'user_id', right_on = 'id')
        club_user_age_df = club_user_age_df[['id_x', 'club_id', 'user_id', 'age']]
        club_user_age_df = club_user_age_df.rename(columns={'id_x':'club_user_id'}).sort_values('club_user_id', ascending=True)
        self.club_user_age_df = club_user_age_df

    # Return the user age df
    def get_user_age_df(self):
        return self.club_user_age_df

    # Merge club_user junction table with club table to get locations of all clubs
    def set_club_locations_df(self):
        club_user_location_df = self.club_user_df.merge(self.club_df, left_on = 'club_id', right_on = 'id')
        club_user_location_df = club_user_location_df[['id_x', 'club_id', 'user_id', 'location']]
        club_user_location_df = club_user_location_df.rename(columns={'id_x':'club_user_id'}).sort_values('club_user_id', ascending=True)
        self.club_user_location_df = club_user_location_df

    # Return the club locations df
    def get_club_locations_df(self):
        return self.club_user_location_df

    # Merge the age df and club df to obtain location and average age of each club
    def set_average_club_age(self):
        average_club_age_df = pd.merge(self.club_user_age_df, self.club_df, left_on='club_id', right_on='id').groupby(['club_id', 'name', 'location'])['age'].mean().reset_index(name = 'average_age')
        self.average_club_age_df = average_club_age_df

    # Return the average club age df
    def get_average_club_age(self):
        return self.average_club_age_df

    # Add column for age difference and sort clubs in ascending order of difference from my age
    def set_age_difference_df(self):
        my_age = float(self.current_user.age)
        average_club_age_df = self.average_club_age_df
        average_club_age_df['age_difference'] = pd.DataFrame(abs(average_club_age_df['average_age'] - my_age))
        average_club_age_difference_df = average_club_age_df.sort_values('age_difference', ascending=True)
        self.average_club_age_difference_df = average_club_age_difference_df

    # Return the club age difference df
    def get_age_difference_df(self):
        return self.average_club_age_difference_df

    # Obtain top 10 closest aged club IDs
    def set_top_10_by_closest_age(self):
        average_club_age_difference_df = self.average_club_age_difference_df
        closest_age_clubs_df = average_club_age_difference_df['club_id'].iloc[0:5]
        self.closest_age_clubs_df = closest_age_clubs_df

    # Return top 10 closest aged club IDs
    def get_top_10_by_closest_age(self):
        return self.closest_age_clubs_df

    # Merge club_user_age_df and club_df to obtain user count of each club
    def set_user_count_per_club(self):
        club_user_count_df = pd.merge(self.club_user_age_df, self.club_df, left_on='club_id', right_on='id').groupby(['club_id', 'name'])['user_id'].count().reset_index(name = 'user_count')
        self.club_user_count_df = club_user_count_df

    def get_user_count_per_club(self):
        return self.club_user_count_df

    # Obtain clubs with matching location (using fuzzy search)
    def set_clubs_with_matching_loc_fuzzy(self):
        club_user_location_df = self.club_user_location_df
        user_id = self.user_id
        user_location = str(self.current_user.city) + ', ' + str(self.current_user.country)
        club_user_location_df['location_match_score'] = np.nan
        no_of_rows = club_user_location_df.shape[0]

        for i in range(no_of_rows):
            match_value = int(fuzz.ratio(user_location, club_user_location_df.iloc[i]['location']))
            if (user_id != club_user_location_df.iloc[i]['user_id']):
                club_user_location_df.iat[i,4] = match_value
            else:
                club_user_location_df.drop(i)

        club_user_location_df = club_user_location_df.sort_values('location_match_score', ascending=False).dropna(how='any',axis=0)
        club_user_location_df = club_user_location_df.drop('club_user_id', axis = 1).groupby(['club_id', 'location', 'location_match_score']).agg(list).reset_index(drop=False)
        club_user_location_df = club_user_location_df[club_user_location_df['location_match_score'] > 60]
        self.club_user_location_df = club_user_location_df

    # Return clubs with matching location
    def get_clubs_with_matching_loc_fuzzy(self):
        return self.club_user_location_df

    # Perform a many-to-many merge to get the favourite books of each club
    def set_club_favourite_books(self):
        club_favourite_books_df = pd.merge(pd.merge(self.club_df, self.club_book_df, left_on='id', right_on='club_id'), 
                    pd.merge(self.book_df, self.club_book_df, left_on='id', right_on='book_id'), on='book_id', how = 'inner') \
                        .groupby(['club_id_x', 'name', 'ISBN'])[['title', 'author']].agg(list).reset_index()

        club_favourite_books_df = club_favourite_books_df.rename(columns={'club_id_x':'club_id'})
        club_favourite_books_df['title'] = club_favourite_books_df['title'].str[0]
        club_favourite_books_df['author'] = club_favourite_books_df['author'].str[0]
        self.club_favourite_books_df = club_favourite_books_df

    #  Return the favourite books of each club
    def get_club_favourite_books(self):
        return self.club_favourite_books_df

    # Perform a many-to-many merge to get the favourite books of each user
    def set_user_club_favourite_books(self):
        user_favourite_books_df = pd.merge(pd.merge(self.user_df, self.user_book_df, left_on='id', right_on='user_id'), 
                    pd.merge(self.book_df, self.user_book_df, left_on='id', right_on='book_id'), on='book_id', how = 'inner') \
                       .groupby(['user_id_x', 'first_name','last_name', 'ISBN', 'title', 'author'])[['title', 'author']].agg(list).reset_index()

        user_favourite_books_df = user_favourite_books_df.rename(columns={'user_id_x':'user_id'})
        user_club_favourite_books_df = pd.merge(user_favourite_books_df, self.club_user_df, left_on="user_id", right_on="user_id", how="inner")
        user_club_favourite_books_df = user_club_favourite_books_df[['club_id', 'user_id', 'title', 'author']]
        user_club_favourite_books_df = user_club_favourite_books_df.sort_values('user_id', ascending=True)
        user_club_favourite_books_df = user_club_favourite_books_df.groupby(['user_id', 'title', 'author']).agg(list).reset_index()
        self.user_club_favourite_books_df = user_club_favourite_books_df

    # Return the favourite books of each user
    def get_user_club_favourite_books(self):
        return self.user_club_favourite_books_df

    # Get the favourite books and authors of the current user
    def set_fav_books_and_authors_per_user(self):
        my_favourite_books_df = self.user_book_df.tail(2)

        book_info_df = pd.merge(my_favourite_books_df, self.book_df, left_on='book_id', right_on='id')
        book_info_df = book_info_df[['user_id', 'title', 'author']]
        book_info_df = book_info_df.sort_values('user_id', ascending=True)
        self.my_favourite_books_df = book_info_df

    # Return the favourite books of the current user
    def get_fav_books_and_authors_per_user(self):
        return self.my_favourite_books_df

    # Get the favourite book titles of the current user with the respective club ids
    def set_club_user_favourite_books(self):
        club_user_favourite_books_df = pd.merge(self.club_favourite_books_df, self.club_user_df, left_on='club_id', right_on='club_id', how='inner')
        club_user_favourite_books_df = club_user_favourite_books_df.drop('id', axis=1).drop('role_num', axis=1)
        club_user_favourite_books_df = club_user_favourite_books_df.groupby(['club_id', 'user_id', 'title', 'name', 'ISBN']).agg(list).reset_index()
        self.club_user_favourite_books_df = club_user_favourite_books_df

    # Return the club user favourite books
    def get_club_user_favourite_books(self):
        return self.club_user_favourite_books_df

    # Obtain all matching favourite book titles between a single user and multiple clubs (using fuzzy search)
    def set_all_favourite_book_matches_fuzzy(self):
        no_of_user_favourite_books = self.my_favourite_books_df.shape[0]
        no_of_club_favourite_books = self.club_user_favourite_books_df.shape[0]
        club_user_title_matches_df = self.club_user_favourite_books_df

        club_user_title_matches_df['title_match_score'] = np.nan

        for i in range(no_of_user_favourite_books):
            my_favourite_book = self.my_favourite_books_df.iloc[i]

            for j in range(no_of_club_favourite_books):
                club_favourite_book = club_user_title_matches_df.iloc[j]

                match_value = int(fuzz.ratio(my_favourite_book['title'], club_favourite_book['title']))
                

                if (self.user_id != club_user_title_matches_df.iloc[j]['user_id']):
                    club_user_title_matches_df.iat[j,6] = match_value
                else:
                    club_user_title_matches_df.drop(j)

        club_user_title_matches_df = club_user_title_matches_df.drop('user_id',axis=1)
        club_user_title_matches_df = club_user_title_matches_df.groupby(['club_id', 'title_match_score', 'title', 'name', 'ISBN']).agg(list).reset_index(drop=False)
        club_user_title_matches_df = club_user_title_matches_df.sort_values('title_match_score', ascending=False).dropna(how='any',axis=0)
        club_user_title_matches_df = club_user_title_matches_df[club_user_title_matches_df['title_match_score'] > 60]
        self.club_user_title_matches_df = club_user_title_matches_df

    # Return all matching favourite book titles between a single user and multiple clubs
    def get_all_favourite_book_matches_fuzzy(self):
        return self.club_user_title_matches_df

    # Obtain a list of clubs in order of which have the most matching favourite book titles with the user
    def set_average_book_match_df(self):
        club_average_book_match_df = self.club_user_title_matches_df.groupby(['club_id', 'name', 'title_match_score'])['title_match_score'] \
            .count().reset_index(name = 'book_match_count') \
            .sort_values('book_match_count', ascending=False) \
            .rename(columns={'name':'club_book_name'})

        self.club_average_book_match_df = club_average_book_match_df

    # Return a list of clubs in order of which have the most matching favourite book titles with the user
    def get_average_book_match_df(self):
        return self.club_average_book_match_df

    # Obtain the favourite authors of the current user with the respective club ids
    def set_club_user_favourite_books_df_2(self):
        club_user_favourite_books_df_2 = pd.merge(self.club_favourite_books_df, self.club_user_df, left_on='club_id', right_on='club_id', how='inner')
        club_user_favourite_books_df_2 = club_user_favourite_books_df_2.drop('id', axis=1).drop('role_num', axis=1)
        club_user_favourite_books_df_2 = club_user_favourite_books_df_2.groupby(['club_id', 'user_id', 'author', 'name', 'ISBN']).agg(list).reset_index()
        self.club_user_favourite_books_df_2 = club_user_favourite_books_df_2

    # Return the favourite authors of the current user with the respective club ids
    def get_club_user_favourite_books_df_2(self):
        return self.club_user_favourite_books_df_2

    # Obtain all matching favourite authors between a single user and multiple clubs (using fuzzy search)
    # This works by checking the authors of all of a club's favourite books agains the authors of all of a user's favourite books
    def set_all_favourite_author_matches_fuzzy(self):

        no_of_user_favourite_books = self.my_favourite_books_df.shape[0]
        no_of_club_favourite_books = self.club_user_favourite_books_df_2.shape[0]
        club_user_author_matches_df = self.club_user_favourite_books_df_2

        club_user_author_matches_df['author_match_score'] = np.nan

        for i in range(no_of_user_favourite_books):
            my_favourite_book = self.my_favourite_books_df.iloc[i]

            for j in range(no_of_club_favourite_books):
                club_favourite_book = club_user_author_matches_df.iloc[j]
                
                match_value = int(fuzz.ratio(my_favourite_book['author'], club_favourite_book['author']))
                # match_value
                if (self.user_id != club_user_author_matches_df.iloc[j]['user_id']):
                    club_user_author_matches_df.iat[j,6] = match_value
                else:
                    club_user_author_matches_df.drop(j)


        club_user_author_matches_df = club_user_author_matches_df.drop('user_id',axis=1)
        club_user_author_matches_df = club_user_author_matches_df.groupby(['club_id', 'author_match_score', 'author', 'name', 'ISBN']).agg(list).reset_index(drop=False)
        club_user_author_matches_df = club_user_author_matches_df.sort_values('author_match_score', ascending=False).dropna(how='any',axis=0)
        club_user_author_matches_df = club_user_author_matches_df[club_user_author_matches_df['author_match_score'] > 80]
        self.club_user_author_matches_df = club_user_author_matches_df

    # Return all matching favourite authors between a single user and multiple clubs
    def get_all_favourite_author_matches_fuzzy(self):
        return self.club_user_author_matches_df

    # Obtain a list of clubs in order of which have the most matching favourite authors with the user
    def set_club_average_author_match_df(self):
        club_average_author_match_df = self.get_all_favourite_author_matches_fuzzy().groupby(['club_id', 'name', 'author_match_score'])['author_match_score'] \
            .count().reset_index(name = 'author_match_count') \
            .sort_values('author_match_count', ascending=False) \
            .rename(columns={'name':'club_author_name'})

        self.club_average_author_match_df = club_average_author_match_df

    # Return a list of clubs in order of which have the most matching favourite authors with the user
    def get_club_average_author_match_df(self):
        return self.club_average_author_match_df

    # Get all columns into one dataframe
    def set_best_clubs_df(self):
        best_clubs_df = self.club_user_count_df.merge(self.average_club_age_difference_df, how = 'left', left_on = 'club_id', right_on = 'club_id')
        best_clubs_df = best_clubs_df.merge(self.club_average_book_match_df, how = 'left', left_on = 'club_id', right_on = 'club_id')
        best_clubs_df = best_clubs_df.merge(self.club_average_author_match_df, how = 'left', left_on = 'club_id', right_on = 'club_id')
        best_clubs_df = best_clubs_df.merge(self.club_user_location_df, how = 'left', left_on = 'club_id', right_on = 'club_id')

        best_clubs_df = best_clubs_df[['club_id', 'location_match_score', 'title_match_score', 'author_match_score', 'age_difference', 'user_count', 'book_match_count', 'author_match_count']]
        best_clubs_df = best_clubs_df.drop('title_match_score',axis=1).drop('author_match_score',axis=1)

        best_clubs_df['title_match_count'] = best_clubs_df['book_match_count'].fillna(0)
        best_clubs_df['author_match_count'] = best_clubs_df['author_match_count'].fillna(0)
        best_clubs_df['location_match_score'] = best_clubs_df['location_match_score'].fillna(0)
        best_clubs_df = best_clubs_df[['club_id', 'age_difference', 'user_count', 'title_match_count', 'author_match_count', 'location_match_score' ]]
        self.best_clubs_df = best_clubs_df

    # Returns the best clubs dataframe
    def get_best_clubs_df(self):
        return self.best_clubs_df

    # Order if location matters (in person clubs)
    def set_best_clubs_in_person_df(self):
        best_clubs_in_person_df = self.best_clubs_df.sort_values(["location_match_score", "title_match_count", "author_match_count", "age_difference", "user_count"], \
            axis = 0, ascending = [False, False, False, True, False], kind='quicksort')
        self.best_clubs_in_person_df = best_clubs_in_person_df.head(18)

    # Return the best clubs in person as a dataframe
    def get_best_clubs_in_person_df(self):
        return self.best_clubs_in_person_df

    # Get the best clubs in person as a list of club ids
    def set_best_clubs_in_person_list(self):
        best_clubs_in_person_list = self.best_clubs_in_person_df['club_id'].tolist()
        best_clubs_in_person_list = best_clubs_in_person_list[:18]
        self.best_clubs_in_person_list = best_clubs_in_person_list
    
    # Return the list of club ids in person
    def get_best_clubs_in_person_list(self):
        return self.best_clubs_in_person_list

    # Order if online only
    def set_best_clubs_online_df(self):
        best_clubs_online_df = self.best_clubs_df.sort_values(["title_match_count", "author_match_count", "age_difference", "user_count"], \
            axis = 0, ascending = [False, False, True, False], kind='quicksort')
        
        self.best_clubs_online_df = best_clubs_online_df.head(18)

    # Return the best clubs online as a dataframe
    def get_best_clubs_online_df(self):
        return self.best_clubs_online_df

    # Get the best clubs online as a list of club ids
    def set_best_clubs_online_list(self):
        best_clubs_online_list = self.best_clubs_online_df['club_id'].tolist()
        best_clubs_online_list = best_clubs_online_list[:18]
        self.best_clubs_online_list = best_clubs_online_list

    # Return the list of club ids online
    def get_best_clubs_online_list(self):
        return self.best_clubs_online_list