#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd


class ClubBookRecommender:
    def __init__(self, club_id_to_query):
        # Load data
        self.df_users = pd.read_csv('clubs/book_to_club_recommender/updated-data-set/clubs_user.csv', encoding='latin1')
        self.df_books = pd.read_csv('clubs/book_to_club_recommender/updated-data-set/clubs_book.csv', encoding='latin1')
        self.df_club_users = pd.read_csv('clubs/book_to_club_recommender/updated-data-set/clubs_club_users.csv')
        self.df_club_books = pd.read_csv('clubs/book_to_club_recommender/updated-data-set/clubs_club_books.csv')

        self.club_id_to_query = club_id_to_query

    def club_average_ages(self):
        # Get average age of each club
        df_club_users_ages = pd.merge(self.df_club_users, self.df_users, left_on='user_id', right_on='id')
        df_club_users_ages = df_club_users_ages[['club_id', 'user_id', 'age']]
        df_club_avg_ages = pd.DataFrame(df_club_users_ages.groupby('club_id')['age'].mean())
        df_club_avg_ages = df_club_avg_ages.reset_index().rename(columns={'age': 'average_age'})
        return df_club_avg_ages

    def club_age_diff(self):
        # Find the difference in average age between the queried club and all other clubs
        df_club_avg_ages = self.club_average_ages()
        queried_club_avg_age = df_club_avg_ages['average_age'][df_club_avg_ages['club_id'] == self.club_id_to_query]
        queried_club_avg_age = queried_club_avg_age.astype(float, errors='raise')
        df_club_avg_ages['age_difference'] = pd.DataFrame(abs(df_club_avg_ages['average_age'] - queried_club_avg_age))
        # Remove the club that is being queried
        df_club_avg_ages.drop(df_club_avg_ages[df_club_avg_ages['club_id'] == self.club_id_to_query].index, inplace=True)
        df_club_avg_ages = df_club_avg_ages.sort_values('age_difference', ascending=True)
        return df_club_avg_ages

    def find_closest_clubs_in_age(self):
        # Find the club(s) with the closest average age to our selected club
        df_club_avg_ages = self.club_age_diff()
        df_closest_club_in_age = df_club_avg_ages['club_id'].iloc[0:2]
        closest_age_clubs_df = df_closest_club_in_age.reset_index().rename(columns={'club_id': 'id'})
        return closest_age_clubs_df

    def get_recommended_books(self):
        # Get favourite books from the above clubs
        df_closest_club_in_age = self.find_closest_clubs_in_age()
        df_closest_club_books = pd.merge(df_closest_club_in_age, self.df_club_books, left_on='id', right_on='club_id')

        recommended_books = pd.merge(df_closest_club_books, self.df_books, left_on='book_id', right_on='id')
        recommended_books.drop(['club_id', 'id_x', 'id_y'], axis=1, inplace=True)
        recommended_books_list = recommended_books['book_id'].tolist()
        return recommended_books_list
