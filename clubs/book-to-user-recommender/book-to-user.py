
import numpy as np
import pandas as pd
from clubs.models import Book, Book_Rating, Club_Users


class BookToUserRecommender:
    def __init__(self):
      
        # load dataset

        self.df_books = pd.DataFrame(list(Book.objects.all().values()))
        self.df_users = pd.DataFrame(list(Club_Users.objects.all().values()))
        self.df_ratings = pd.DataFrame(list(Book_Rating.objects.all().values()))

        # removing 0-rating from dataframe
        self.df_ratings.drop(self.df_ratings[self.df_ratings['rating'] == 0].index, inplace=True) 
    

        # columns to keep 
        # self.df_books_cleaned = pd.DataFrame(self.df_books[['ISBN','title', 'author','publication_year','publisher']])

        # removing nan's 
        # self.df_books_cleaned =  self.df_books_cleaned.dropna(how='any', inplace=True)

        # save books that are published between 1950 to 2016
        # self.df_books_cleaned = self.df_books_cleaned[(self.df_books_cleaned['publication_year'] > 1950) & (self.df_books_cleaned['publication_year'] <= 2016)]

        # regex-based replacement of certain characters
        # self.df_books_cleaned['author'] = self.df_books_cleaned['author'].str.replace(r'[^\w\s]+', '')


    # experimental layout for implementation


    def set_age_constraint(self):
        self.df_users_cleaned = pd.DataFrame(self.df_users[self.df_users['age']<=100])


    def set_columns_to_keep(self):
        # columns to keep
        self.df_books_cleaned = pd.DataFrame(self.df_books[['ISBN','title', 'author','publication_year','publisher']])

    def set_publication_year(self):
        # save books that are published between 1950 to 2016
        self.df_books_cleaned = self.df_books_cleaned[(self.df_books_cleaned['publication_year'] > 1950)
             & (self.df_books_cleaned['publication_year'] <= 2016)]

    def set_character_replacement(self):
        # regex-based replacement of certain characters
        self.df_books_cleaned['author'] = self.df_books_cleaned['author'].str.replace(r'[^\w\s]+', '')

    def get_top_books(self):
        # get the top 20 highest rated books
        top_20_books = self.df_ratings.groupby('ISBN').agg(['mean', 'count'])['Book-Rating'].reset_index()

        # generate score based on mean rating and total number of times the book is rated
        minVotes = top_20_books['count'].quantile(0.10) # minimum votes required to be listed in the Top 250
        top_20_books = top_20_books[top_20_books['count']>minVotes]
        print('minimum votes = ', minVotes)
        print(top_20_books.shape)
        R = top_20_books['mean'] # average for the book (mean) = (Rating)
        v = top_20_books['count'] # number of votes for the book = (votes)
        C = top_20_books['mean'].mean() # mean vote across all books
        top_20_books['weighted rating'] = (v/(v+minVotes))*R + (minVotes/(v+minVotes))*C
        top_20_books = top_20_books.sort_values('weighted rating', ascending=False).reset_index(drop=True)

        # get title of books
        top_20_books = pd.merge(top_20_books, self.df_books_cleaned, on='ISBN')[['title', 'author', 'mean', 'count', 'weighted rating', 
                              'publication_year']].drop_duplicates('title').iloc[:20]
        return top_20_books


    def get_top_authors(self):
        # top 20 highest rated authors

        # drop any duplicates
        self.df_books_cleaned = self.df_books_cleaned.drop_duplicates(['author', 'title'])

        # get book-author and title
        highest_rated_author = pd.merge(self.df_books_cleaned, self.df_ratings_cleaned, on='ISBN')[['author', 'Book-Rating', 'title', 'ISBN']]

        highest_rated_author = highest_rated_author.groupby('author').agg(['mean', 'count'])['Book-Rating'].reset_index()

        # generate score based on mean rating and total number of times the author is rated
        m = highest_rated_author['count'].quantile(0.6) # minimum votes required to be listed in the top
        highest_rated_author = highest_rated_author[highest_rated_author['count']>m]
        print('minimum votes =', m)
        print(highest_rated_author.shape)
        R = highest_rated_author['mean'] # average for the author (mean) = (Rating)
        v = highest_rated_author['count'] # number of votes for the author = (votes)
        C = highest_rated_author['mean'].mean() # mean vote across all authors
        highest_rated_author['weighted rating'] = (v/(v+m))*R + (m/(v+m))*C
        highest_rated_author = highest_rated_author.sort_values('weighted rating', ascending=False).reset_index(drop=True)

        return highest_rated_author.iloc[:20]


    def get_user_prediction(self):
        # get the prediction of book to recommend
        pass   


    def get_recommended_books(self):
        # get the top 10 most popular authors
        pass
