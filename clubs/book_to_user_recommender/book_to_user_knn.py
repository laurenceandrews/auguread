import csv
import heapq
import os
from collections import defaultdict
from operator import itemgetter

import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
from clubs.models import Book, Book_Rating, User
from surprise import (SVD, BaselineOnly, Dataset, KNNBasic, NormalPredictor,
                      Reader)
from surprise.model_selection import cross_validate


class BookToUserRecommender:
    def __init__(self, user_id_to_query):

        self.df_books = pd.DataFrame(list(Book.objects.all().values()))
        self.df_users = pd.DataFrame(list(User.objects.all().values()))
        self.df_ratings = pd.DataFrame(list(Book_Rating.objects.all().values()))

        self.df_ratings.drop(self.df_ratings[self.df_ratings['rating'] == 0].index, inplace=True)
        self.df_books = self.df_books.dropna(how='any')
        self.df_ratings = self.df_ratings.dropna(how='any')

        # Set user as test subject
        self.test_subject = user_id_to_query

        # New way
        self.reader = Reader(rating_scale=(1, 10))
        self.dataset = Dataset.load_from_df(self.df_ratings[['user_id', 'book_id', 'rating']], self.reader)

        # Build a full Surprise training set from dataset
        self.trainset = self.dataset.build_full_trainset()

        # Set no of items to recommend
        self.k = 10

        self.recommendations = []
        self.test_subject_iid = 0

    def create_similarity_matrix(self):
        # similarity_matrix = BaselineOnly()\
        # .fit(self.trainset)\
        # .compute_similarities()

        # similarity_matrix = NormalPredictor()\
        # .fit(self.trainset)\
        # .compute_similarities()

        # similarity_matrix = SVD()\
        # .fit(self.trainset)\
        # .compute_similarities()

        similarity_matrix = KNNBasic()\
            .fit(self.trainset)\
            .compute_similarities()

        return similarity_matrix

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
        test_subject_ratings = self.trainset.ur[self.test_subject_iid]
        k_neighbors = heapq.nlargest(self.k, test_subject_ratings, key=lambda t: t[1])
        return k_neighbors

    def create_default_dict(self):
        # Default dict is basically a standard dictionary,
        # the difference beeing that it doesn't throw an error
        # when trying to access a key which does not exist,
        # instead a new entry, with that key, is created.
        similarity_matrix = self.create_similarity_matrix()
        candidates = defaultdict(float)
        k_neighbors = self.get_top_k_items_rated()

        for itemID, rating in k_neighbors:
            try:
                self.similaritities = similarity_matrix[itemID]
                for innerID, score in enumerate(self.similaritities):
                    candidates[innerID] += score * (rating / 5.0)
            except:
                continue
        return candidates

    def build_dictionary(self):

        self.create_inner_id()
        candidates = self.create_default_dict()

        # Build a dictionary of books the user has read
        read = {}
        for self.itemID, self.rating in self.trainset.ur[self.test_subject_iid]:
            read[self.itemID] = 1

        # Add items to list of user's recommendations
        # If they are similar to their favorite books,
        # AND have not already been read.
        self.recommendations = []

        position = 0
        for self.itemID, self.rating_sum in sorted(candidates.items(), key=itemgetter(1), reverse=True):
            if not self.itemID in read:
                self.recommendations.append(self.trainset.to_raw_iid(self.itemID))  # Adding the book id to the rec list
                position += 1
                if (position > 10):
                    break  # We only want top 10

        return self.recommendations

    def get_recommended_books(self):
        return self.recommendations
