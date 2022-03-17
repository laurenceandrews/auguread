#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
from clubs.models import Book, Book_Rating, Club_Books, Club_Users


class ClubBookAuthorRecommender:
    def __init__(self, club_id_to_query):
        # Load data
        self.df_books = pd.DataFrame(list(Book.objects.all().values()))
        self.df_club_users = pd.DataFrame(list(Club_Users.objects.all().values()))
        self.df_club_books = pd.DataFrame(list(Club_Books.objects.all().values()))

        self.df_book_ratings = pd.DataFrame(list(Book_Rating.objects.all().values()))
        self.df_book_ratings.drop(self.df_book_ratings[self.df_book_ratings['rating'] == 0].index, inplace=True)

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
        df_favourite_books = self.df_club_books[self.df_club_books['club_id'] == int(self.club_id_to_query)]
        # Get book info of the club's favourite books
        df_favourite_books = pd.merge(df_favourite_books, self.df_books, left_on='book_id', right_on='id')
        return df_favourite_books

    def getFavBooksAuthors(self):
        df_favourite_books = self.getClubFavBooks()
        # Get authors of the favourite books
        df_fav_authors = df_favourite_books['author']
        return df_favourite_books, df_fav_authors

    def getAuthorBooks(self):
        # Get all books by the favourite authors
        df_favourite_books, df_fav_authors = self.getFavBooksAuthors()
        df_author_books = pd.merge(self.df_books, df_fav_authors, on='author')
        # Exclude the books that are from the club's favourite books
        df_author_books = df_author_books[~df_author_books.ISBN.isin(df_favourite_books.ISBN)]
        return df_author_books

    def author_books_is_empty(self):
        author_books = self.getAuthorBooks()
        return len(author_books) == 0

    def get_recommended_books(self):
        df_author_books = self.getAuthorBooks()
        # Get the most rated books from the above list
        df_author_book_ratings = pd.merge(self.df_book_ratings, df_author_books, left_on='book_id', right_on='id')
        df_author_books_rating_count = pd.DataFrame(df_author_book_ratings.groupby('book_id')['rating'].count())

        # Make Rating count as a regular column and sort
        df_author_books_rating_count.reset_index(level=0, inplace=True)
        df_author_books_rating_count.sort_values('rating', ascending=False)

        recommended_books = pd.DataFrame(df_author_books_rating_count['book_id'].iloc[0:10])
        recommended_books = pd.merge(recommended_books, self.df_books, left_on='book_id', right_on='id')

        recommended_books_list = recommended_books['id'].tolist()
        return recommended_books_list
