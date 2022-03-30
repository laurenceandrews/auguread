import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

import sys
print(sys.prefix)

from surprise import KNNBasic
from surprise import Dataset
from surprise import Reader
from surprise.model_selection import cross_validate

from collections import defaultdict
from operator import itemgetter
import heapq

import os
import csv

from clubs.models import Book, Book_Rating, User


class BookToUserRecommender:
    def __init__(self):

        # Old way of loading dataset
        self.df_books = pd.DataFrame(list(Book.objects.all().values()))
        self.df_users = pd.DataFrame(list(User.objects.all().values()))
        self.df_ratings = pd.DataFrame(list(Book_Rating.objects.all().values()))

        self.df_ratings.drop(self.df_ratings[self.df_ratings['rating'] == 0].index, inplace=True)
        self.df_books = self.df_books.dropna(how='any')
        self.df_ratings = self.df_ratings.dropna(how='any')

        reader = Reader(rating_scale=(1, 10))

        # Loading the dataset from the dataframe
        self.dataset = Dataset.load_from_df(self.df_ratings[['id', 'book_id', 'user_id', 'rating']], reader)

        # Build a full Surprise training set from dataset
        self.trainset = self.dataset.build_full_trainset()

        # Set no of items to recommend
        self.k = 10

        # Set user as test subject
        self.get_test_subject = 12345

    def create_similarity_matrix(self):
        self.similarity_matrix = KNNBasic(sim_options={
        'name': 'cosine',
        'user_based': False
        })\
        .fit(self.trainset)\
        .compute_similarities()

    def create_inner_id(self):
        # When using Surprise, there are RAW and INNER IDs.
        # Raw IDs are the IDs, strings or numbers, you use when
        # creating the trainset. The raw ID will be converted to
        # an unique integer Surprise can more easily manipulate
        # for computations.
        #
        # So in order to find an user inside the trainset, you
        # need to convert their RAW ID to the INNER Id. Read
        # here for more info https://surprise.readthedocs.io/en/stable/FAQ.html#what-are-raw-and-inner-ids
        self.test_subject_iid = self.trainset.to_inner_uid(self.test_subject)

    def get_top_k_items_rated(self):
        # Get the top K items we rated
        self.test_subject_ratings = self.trainset.ur[self.test_subject_iid]
        self.k_neighbors = heapq.nlargest(self.k, self.test_subject_ratings, key=lambda t: t[1])

    def create_default_dict(self):
        # Default dict is basically a standard dictionary,
        # the difference beeing that it doesn't throw an error
        # when trying to access a key which does not exist,
        # instead a new entry, with that key, is created.
        self.candidates = defaultdict(float)

        for itemID, rating in self.k_neighbors:
            try:
                self.similaritities = self.similarity_matrix[itemID]
                for innerID, score in enumerate(self.similaritities):
                    self.candidates[innerID] += score * (rating / 5.0)
            except:
                continue

    # Utility we'll use later.
    def get_book_name(self, bookID):
        if (bookID) in self.bookID_to_name:
            return self.bookID_to_name[bookID]
        else:
            return ""

    def build_dictionary(self):
        # Build a dictionary of books the user has read
        read = {}
        for self.itemID, self.rating in self.trainset.ur[self.test_subject_iid]:
            self.read[self.itemID] = 1

        # Add items to list of user's recommendations
        # If they are similar to their favorite books,
        # AND have not already been read.
        recommendations = []

        position = 0
        for self.itemID, self.rating_sum in sorted(self.candidates.items(), key=itemgetter(1), reverse=True):
            if not self.itemID in read:
                recommendations.append(self.get_book_namee(self, self.itemID))
                position += 1
                if (position > 10): break # We only want top 10

        for rec in self.recommendations:
            print("book: ", rec)