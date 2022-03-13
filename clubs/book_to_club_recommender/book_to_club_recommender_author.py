#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
from clubs.models import Book, Club_Books, Club_Users


class ClubBookAuthorRecommender:
    def __init__(self, club_id_to_query):
        # Load data
        self.df_books = pd.DataFrame(list(Book.objects.all().values()))
        self.df_club_users = pd.DataFrame(list(Club_Users.objects.all().values()))
        self.df_club_books = pd.DataFrame(list(Club_Books.objects.all().values()))

        self.df_book_ratings = pd.read_csv('clubs/dataset/BX-Book-Ratings.csv', encoding='latin1', sep=';')
        self.df_book_ratings.drop(self.df_book_ratings[self.df_book_ratings['Book-Rating'] == 0].index, inplace=True)

        self.club_id_to_query = club_id_to_query

    def getUserRatingCount(self):
        # Find the number of ratings made by each user
        df_rating_count = pd.DataFrame(self.df_book_ratings.groupby('User-ID')['Book-Rating'].count())

        # Make Rating count as a regular column
        df_rating_count.reset_index(level=0, inplace=True)

        # Remove from the ratings table, all users with less than 20 ratings
        df_rating_count.drop(df_rating_count[df_rating_count['Book-Rating'] < 20].index, inplace=True)
        df_rating_count.drop('Book-Rating', axis=1, inplace=True)
        return df_rating_count

    def getRatingInfo(self):
        df_rating_count = self.getUserRatingCount()
        self.self.df_book_ratings = pd.merge(self.df_book_ratings, df_rating_count, on='User-ID')
        return self.df_book_ratings

    def getClubFavBooks(self):
        # Get the favourite books of the club specified
        df_favourite_books = pd.DataFrame(self.df_club_books['book_id'][self.df_club_books['club_id'] == self.club_id_to_query])

        # Get ISBNs of the club's favourite books
        df_favourite_books = pd.merge(df_favourite_books, self.df_books, left_on='book_id', right_on='id')
        return df_favourite_books

    def getFavBooksAuthors(self):
        df_favourite_books = self.getClubFavBooks()
        # Get ISBNs and authors of the favourite books
        fav_authors = df_favourite_books['author'].tolist()
        return df_favourite_books, fav_authors

    def getAuthorBooks(self):
        # Get all books by the favourite authors
        df_all_author_books = pd.DataFrame()
        df_favourite_books, fav_authors = self.getFavBooksAuthors()

        for author in fav_authors:
            df_author_books = pd.DataFrame(self.df_books['ISBN'][self.df_books['author'] == author])
            # Exclude the books that are from the club's favourite books
            df_author_books = df_author_books[~df_author_books.ISBN.isin(df_favourite_books.ISBN)]
            df_all_author_books = pd.concat([df_all_author_books, df_author_books])

        return df_all_author_books

    def author_books_is_empty(self):
        author_books = self.getAuthorBooks()
        return len(author_books) == 0

    def get_recommended_books(self):
        df_all_author_books = self.getAuthorBooks()

        # Get the most rated books from the above list
        df_author_book_ratings = pd.merge(df_all_author_books, self.df_book_ratings, left_on='ISBN', right_on='ISBN')
        df_author_books_rating_count = pd.DataFrame(df_author_book_ratings.groupby('ISBN')['Book-Rating'].count())

        # Make Rating count as a regular column and sort
        df_author_books_rating_count.reset_index(level=0, inplace=True)
        df_author_books_rating_count.sort_values('Book-Rating', ascending=False)

        recommended_books = df_author_books_rating_count['ISBN'].iloc[0:10]
        recommended_books = pd.merge(recommended_books, self.df_books, on='ISBN')
        recommended_books_list = recommended_books['book_id'].tolist()
        return recommended_books_list
