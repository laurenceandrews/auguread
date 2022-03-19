
import numpy as np
import pandas as pd
from clubs.models import Book, Book_Rating, Club_Books, Club_Users


class BookToUserRecommender:
    def __init__(self):
      
        # load dataset

        self.df_books = pd.DataFrame(list(Book.objects.all().values()))
        self.df_users = pd.DataFrame(list(Club_Users.objects.all().values()))
        self.df_ratings = pd.DataFrame(list(Book_Rating.objects.all().values()))

        # removing 0-rating from dataframe
        self.df_book_ratings.drop(self.df_book_ratings[self.df_book_ratings['rating'] == 0].index, inplace=True) 

        # columns to keep 
        self.df_books_cleaned = pd.DataFrame(self.df_books[['ISBN','title', 'author','publication_year','publisher']])

        # removing nan's 
        self.df_books_cleaned =  self.df_books_cleaned.dropna(how='any', inplace=True)

        # save books that are published between 1950 to 2016
        self.df_books_cleaned = self.df_books_cleaned[(self.df_books_cleaned['publication_year'] > 1950) & (self.df_books_cleaned['publication_year'] <= 2016)]

        # regex-based replacement of certain characters
        self.df_books_cleaned['author'] = self.df_books_cleaned['author'].str.replace(r'[^\w\s]+', '')


    # experimental layout for implementation


    def set_dataframe_restraints(self):
        # place above df restraints in setter's


     def set_age_constraint(self):
         self.df_users_cleaned = pd.DataFrame(self.df_users[self.df_users['age']<=100])


    def get_top_books(self):
        # get the top 20 highest rated books
        pass


    def get_top_authors(self):
        # get the top 20 most popular authors
        pass


    def get_user_prediction(self):
        # get the prediction of book to recommend
        pass   


    def get_recommended_books(self):
        # get the top 10 most popular authors
        pass
