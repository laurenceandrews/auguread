#!/usr/bin/env python
# coding: utf-8
# converted from a Jupyter notebook

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import scipy.sparse.linalg as spla
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
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

    def get_user(self):
        current_user = User.objects.get(pk=self.user_id)
        return current_user

    # Merge club_user junction table with user table to get ages of all users
    def get_user_age_df(self):
        club_user_age_df = self.club_user_df.merge(self.user_df, left_on = 'user_id', right_on = 'id')
        club_user_age_df = club_user_age_df[['id_x', 'club_id', 'user_id', 'age']]
        club_user_age_df = club_user_age_df.rename(columns={'id_x':'club_user_id'}).sort_values('club_user_id', ascending=True)
        return club_user_age_df

    # Merge club_user junction table with club table to get locations of all clubs
    def get_club_locations_df(self):
        club_user_location_df = self.club_user_df.merge(self.club_df, left_on = 'club_id', right_on = 'id')
        club_user_location_df = club_user_location_df[['id_x', 'club_id', 'user_id', 'location']]
        club_user_location_df = club_user_location_df.rename(columns={'id_x':'club_user_id'}).sort_values('club_user_id', ascending=True)
        return club_user_location_df

    # Get location and average age of each club
    def get_average_club_age(self):
        average_club_age_df = pd.merge(self.get_user_age_df(), self.club_df, left_on='club_id', right_on='id').groupby(['club_id', 'name', 'location'])['age'].mean().reset_index(name = 'average_age')
        return average_club_age_df

    # Add column for age difference and return clubs in ascending order of difference from my age
    def get_age_difference_df(self):
        my_age = float(self.get_user().age)
        average_club_age_df = self.get_average_club_age()
        average_club_age_df['age_difference'] = pd.DataFrame(abs(average_club_age_df['average_age'] - my_age))
        average_club_age_difference_df = average_club_age_df.sort_values('age_difference', ascending=True)
        return average_club_age_difference_df

    # Return top 10 closest aged club IDs
    def get_top_10_by_closest_age(self):
        average_club_age_difference_df = self.get_age_difference_df()
        closest_age_clubs_df = average_club_age_difference_df['club_id'].iloc[0:5]
        return closest_age_clubs_df

    # Get user count of each club
    def get_user_count_per_club(self):
        club_user_count_df = pd.merge(self.get_user_age_df(), self.club_df, left_on='club_id', right_on='id').groupby(['club_id', 'name'])['user_id'].count().reset_index(name = 'user_count')
        return club_user_count_df

    # Return clubs with matching location (using fuzzy search)
    def get_clubs_with_matching_loc_fuzzy(self):
        user_location = "Tokyo, Japan"
        user_id = self.user_id

        club_user_location_df['location_match_score'] = np.nan
        club_user_location_df

        no_of_rows = club_user_location_df.shape[0]

        for i in range(no_of_rows):
            match_value = int(fuzz.token_sort_ratio(user_location, club_user_location_df.iloc[i]['location']))
            if (user_id != club_user_location_df.iloc[i]['user_id']):
                club_user_location_df.iat[i,4] = match_value
            else:
                club_user_location_df.drop(i)

        club_user_location_df = club_user_location_df.sort_values('location_match_score', ascending=False).dropna(how='any',axis=0)
        club_user_location_df = club_user_location_df.drop('club_user_id', axis = 1).groupby(['club_id', 'location', 'location_match_score']).agg(list).reset_index()
        club_user_location_df = club_user_location_df[club_user_location_df['location_match_score'] > 80]

        return club_user_location_df


    # Perform a many-to-many merge to get the favourite books of each club
    def get_club_favourite_books(self):
        club_favourite_books_df = pd.merge(pd.merge(self.club_df, self.club_book_df, left_on='id', right_on='club_id'), 
                    pd.merge(self.book_df, self.club_book_df, left_on='id', right_on='book_id'), on='book_id', how = 'inner') \
                        .groupby(['club_id_x', 'name', 'ISBN'])['title', 'author'].agg(list).reset_index()

        club_favourite_books_df = club_favourite_books_df.rename(columns={'club_id_x':'club_id'})

        club_favourite_books_df['title'] = club_favourite_books_df['title'].str[0]
        club_favourite_books_df['author'] = club_favourite_books_df['author'].str[0]

        return club_favourite_books_df

    # Perform a many-to-many merge to get the favourite books of each user
    def get_user_club_favourite_books(self):
        user_favourite_books_df = pd.merge(pd.merge(self.user_df, self.user_book_df, left_on='id', right_on='user_id'), 
                    pd.merge(self.book_df, self.user_book_df, left_on='id', right_on='book_id'), on='book_id', how = 'inner') \
                       .groupby(['user_id_x', 'first_name','last_name', 'ISBN', 'title', 'author'])['title', 'author'].agg(list).reset_index()

        user_favourite_books_df = user_favourite_books_df.rename(columns={'user_id_x':'user_id'}).drop(0, 1)
        user_favourite_books_df
        user_club_favourite_books_df = pd.merge(user_favourite_books_df, self.club_user_df, left_on="user_id", right_on="user_id", how="inner")
        user_club_favourite_books_df = user_club_favourite_books_df[['club_id', 'user_id', 'title', 'author']]
        user_club_favourite_books_df = user_club_favourite_books_df.sort_values('user_id', ascending=True)
        user_club_favourite_books_df = user_club_favourite_books_df.groupby(['user_id', 'title', 'author']).agg(list).reset_index()
        return user_club_favourite_books_df

    # Get the favourite books and authors of one user (me)
    def get_fav_books_and_authors_per_user(self):
        my_id = self.user_id
        my_favourite_books_df = self.get_user_club_favourite_books().loc[self.get_user_club_favourite_books()['user_id'] == my_id]
        return my_favourite_books_df

    def get_club_user_favourite_books(self):
        club_user_favourite_books_df = pd.merge(self.get_club_favourite_books(), self.club_user_df, left_on='club_id', right_on='club_id', how='inner')
        club_user_favourite_books_df = club_user_favourite_books_df.drop('id', axis=1).drop('role_num', axis=1)
        club_user_favourite_books_df = club_user_favourite_books_df.groupby(['club_id', 'user_id', 'title', 'name', 'ISBN']).agg(list).reset_index()
        return club_user_favourite_books_df

    # Return all matching favourite books between a single user and multiple clubs (using fuzzy search)

    def get_all_favourite_book_matches_fuzzy(self):
        no_of_user_favourite_books = self.get_fav_books_and_authors_per_user().shape[0]
        no_of_club_favourite_books = self.get_club_user_favourite_books().shape[0]
        club_user_title_matches_df = self.get_club_user_favourite_books()

        club_user_title_matches_df['title_match_score'] = np.nan
        club_user_title_matches_df

        for i in range(no_of_user_favourite_books):
            my_favourite_book = self.get_fav_books_and_authors_per_user().iloc[i]

            for j in range(no_of_club_favourite_books):
                club_favourite_book = club_user_title_matches_df.iloc[j]

                match_value = int(fuzz.token_sort_ratio(my_favourite_book['title'], club_favourite_book['title']))
                club_user_title_matches_df.iat[j,6] = match_value

                if (self.user_id != club_user_title_matches_df.iloc[j]['user_id']):
                    club_user_title_matches_df.iat[j,6] = match_value
                else:
                    club_user_title_matches_df.drop(j)


        club_average_title_match_df = club_user_title_matches_df[['club_id', 'title_match_score', 'title', 'name', 'ISBN']]
        club_user_title_matches_df = club_user_title_matches_df.drop('user_id',axis=1)
        club_user_title_matches_df = club_user_title_matches_df.groupby(['club_id', 'title_match_score', 'title', 'name', 'ISBN']).agg(list).reset_index()
        club_user_title_matches_df = club_user_title_matches_df.sort_values('title_match_score', ascending=False).dropna(how='any',axis=0)
        club_user_title_matches_df = club_user_title_matches_df[club_user_title_matches_df['title_match_score'] > 40]

        return club_user_title_matches_df

    # Return a list of clubs in order of which have the most matching favourite books with the user
    def get_average_book_match_df(self):
        club_average_book_match_df = self.get_all_favourite_book_matches_fuzzy().groupby(['club_id', 'name', 'title_match_score'])['title_match_score'] \
            .count().reset_index(name = 'book_match_count') \
            .sort_values('book_match_count', ascending=False) \
            .rename(columns={'name':'club_book_name'})

        return club_average_book_match_df


    def get_club_user_favourite_books_df_2(self):
        club_user_favourite_books_df_2 = pd.merge(self.get_club_favourite_books(), self.club_user_df, left_on='club_id', right_on='club_id', how='inner')
        club_user_favourite_books_df_2 = club_user_favourite_books_df_2.drop('id', axis=1).drop('role_num', axis=1)
        club_user_favourite_books_df_2 = club_user_favourite_books_df_2.groupby(['club_id', 'user_id', 'author', 'name', 'ISBN']).agg(list).reset_index()
        club_user_favourite_books_df_2

    # Return all matching favourite authors between a single user and multiple clubs (using fuzzy search)
    # This works by checking the authors of all of a club's favourite books agains the authors of all of a user's favourite books
    def get_all_favourite_author_matches_fuzzy(self):
        user_id = self.user_id

        no_of_user_favourite_books = self.get_fav_books_and_authors_per_user().shape[0]
        no_of_club_favourite_books = self.get_club_user_favourite_books_df_2().shape[0]
        club_user_author_matches_df = self.get_club_user_favourite_books_df_2()

        club_user_author_matches_df['author_match_score'] = np.nan

        for i in range(no_of_user_favourite_books):
            my_favourite_book = self.get_fav_books_and_authors_per_user().iloc[i]
            

            for j in range(no_of_club_favourite_books):
                club_favourite_book = club_user_author_matches_df.iloc[j]
                
                match_value = int(fuzz.token_sort_ratio(my_favourite_book['author'], club_favourite_book['author']))
                # match_value
                club_user_author_matches_df.iat[j,6] = match_value


                # if (user_id != club_user_author_matches_df.iloc[j]['user_id']):
                #     club_user_author_matches_df.iat[j,7] = match_value
                # else:
                #     club_user_author_matches_df.drop(j)


        club_average_author_match_df = club_user_author_matches_df[['club_id', 'author_match_score', 'author', 'name', 'ISBN']]
        club_user_author_matches_df = club_user_author_matches_df.drop('user_id',axis=1)
        club_user_author_matches_df = club_user_author_matches_df.groupby(['club_id', 'author_match_score', 'author', 'name', 'ISBN']).agg(list).reset_index()
        club_user_author_matches_df = club_user_author_matches_df.sort_values('author_match_score', ascending=False).dropna(how='any',axis=0)
        club_user_author_matches_df = club_user_author_matches_df[club_user_author_matches_df['author_match_score'] > 40]

        return club_user_author_matches_df

    # Return a list of clubs in order of which have the most matching favourite authors with the user

    def get_club_average_author_match_df(self):
        club_average_author_match_df = self.get_all_favourite_author_matches_fuzzy().groupby(['club_id', 'name'])['match_score'].count().unstack(fill_value=0).stack().reset_index(name = 'author_match_count').sort_values('author_match_count', ascending=False).rename(columns={'name':'club_author_name'})
        return club_average_author_match_df

    # Get all columns into one dataframe

    # Location: average_club_age_difference_df
    # Age difference: average_club_age_difference_df
    # User count: club_user_count_df
    # Favourite books: club_average_book_match_df
    # Favourite authors: club_average_author_match_df
    def get_best_clubs_df(self):
        best_clubs_df = self.get_user_count_per_club().merge(self.get_age_difference_df(), how = 'left', left_on = 'club_id', right_on = 'club_id')
        best_clubs_df = best_clubs_df.merge(self.get_average_book_match_df(), how = 'left', left_on = 'club_id', right_on = 'club_id')
        best_clubs_df = best_clubs_df.merge(self.get_club_average_author_match_df(), how = 'left', left_on = 'club_id', right_on = 'club_id')
        best_clubs_df = best_clubs_df.merge(self.get_clubs_with_matching_loc_fuzzy(), how = 'left', left_on = 'club_id', right_on = 'club_id')

        best_clubs_df = best_clubs_df[['club_id', 'club_author_name', 'location', 'age_difference', 'user_count', 'book_match_count', 'author_match_count', 'matching_location']]
        best_clubs_df = best_clubs_df.rename(columns={'club_author_name':'club_name'})

        best_clubs_df['book_match_count'] = best_clubs_df['book_match_count'].fillna(0)
        best_clubs_df['author_match_count'] = best_clubs_df['author_match_count'].fillna(0)

        # Dirty way of getting name back...
        best_clubs_df = best_clubs_df.merge(self.get_age_difference_df(), on = 'club_id')
        best_clubs_df = best_clubs_df[['club_id', 'name', 'location_x', 'age_difference_y', 'user_count', 'book_match_count', 'author_match_count', 'matching_location']]
        best_clubs_df = best_clubs_df.rename(columns={'location_x':'location', 'age_difference_y':'age_difference'} )

        return best_clubs_df


    # <h3><b>To do</b></h3>
    # <p>Implement algorithm which recommends 10 clubs based on user count, average age, location,
    # favourite books and favourite authors</p>
    # <br>
    # <b>Weighting if online only checkbox checked:</b>
    # <ul>
    # <li>Favourite books 0.3</li>
    # <li>Favourite authors 0.3</li>
    # <li>User count: 0.2</li>
    # <li>Average age: 0.1</li>
    # <li>Location 0.1</li>
    # </ul>
    # <br>
    # <b>Weighting if online only checkbox <i>un</i>checked:</b>
    # <ul>
    # <li>Location 0.4</li>
    # <li>Favourite books 0.2</li>
    # <li>Favourite authors 0.2</li>
    # <li>User count: 0.1</li>
    # <li>Average age: 0.1</li>
    # </ul>

    # Order if location matters

    # TO DO: Find a way to convert location to distance
    def get_best_clubs_in_person(self):
        best_clubs_in_person_df = self.get_best_clubs_df().sort_values(["matching_location", "book_match_count", "author_match_count", "age_difference", "user_count"], ascending = [False, False, False, True, False])
        best_clubs_in_person_list = best_clubs_in_person_df['club_id'].tolist()
        print(best_clubs_in_person_list)
        # return best_clubs_in_person_list

    # Order if online only
    def get_best_clubs_online(self):
        best_clubs_online_df = self.get_best_clubs_df().sort_values(["book_match_count", "author_match_count", "age_difference", "user_count"], ascending = [False, False, True, False])
        best_clubs_online_list = best_clubs_online_df['club_id'].tolist()
        return best_clubs_online_list
