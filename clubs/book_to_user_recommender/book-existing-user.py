import pandas as pd
import numpy as np
import tensorflow as tf 
from sklearn.preprocessing import MinMaxScaler
from clubs.models import Book, Book_Rating, User


class BookToExistingUserRecommender:
    def __init__(self):

        # load datasets

        self.df_books = pd.DataFrame(list(Book.objects.all().values()))
        self.df_users = pd.DataFrame(list(User.objects.all().values()))
        self.df_ratings = pd.DataFrame(list(Book_Rating.objects.all().values()))

        self.df_ratings.drop(self.df_ratings[self.df_ratings['rating'] == 0].index, inplace=True)
        self.df_books = self.df_books.dropna(how='any')
        self.df_ratings = self.df_ratings.dropna(how='any')
    
      # experimental layout for implementation  

    def get_merged_datasets(self):
        # merge user rating and book data
        book_rating = pd.merge(self.df_ratings, self.df_books, on='ISBN')
        return book_rating
    

    def get_filtered_ratings(self):
        # filtering books that have had => 15 ratings
        rating_count = (book_rating.
        groupby(by = ['title'])['Book-Rating'].
        count().
        reset_index().
        rename(columns = {'Book-Rating': 'RatingCount_book'})
        [['title', 'RatingCount_book']]
        )

        threshold = 15
        rating_count = rating_count.query('RatingCount_book >= @threshold')
        return rating_count 

    def get_merged_user_rating(self):
        rating_count = self.get_filtered_ratings()
        book_rating = self.get_merged_datasets()
        user_rating = pd.merge(rating_count, book_rating, left_on='title', right_on='title', how='left')
        return user_rating