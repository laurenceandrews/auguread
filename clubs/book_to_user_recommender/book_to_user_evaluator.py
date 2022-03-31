#!/usr/bin/env python
# coding: utf-8


from surprise import SVD
from surprise import KNNBasic
from surprise import BaselineOnly
from surprise import NormalPredictor

from surprise import Reader
from surprise import Dataset
from surprise.model_selection import cross_validate

import csv

class BookToUserEvaluator:

    def __init__(self):

        # Load in the book ratings as a dataset
        reader = Reader(line_format='user item rating', sep=';', skip_lines=1)
        self.ratings_dataset = Dataset.load_from_file('ratings_no_quotes_smallest.csv', reader=reader)

        # Lookup a book's name with it's bookID as key
        self.bookID_to_name = {}
        with open('./clubs_book.csv', newline='', encoding='Latin1') as csvfile:
                book_reader = csv.reader(csvfile)
                next(book_reader)
                for row in book_reader:
                    bookID = int(row[0]) 
                    book_name = row[1]
                    self.bookID_to_name[bookID] = book_name


    def svd_evaluation(self):  
        # SVD provides a more accurate prediction but only if applied on preprocessed data
        # In the example below, SVD has a low RMSE and MAE, but takes longer to fit
        algo = SVD()

        # Run 5-fold cross-validation and print results.
        cross_validate(algo, self.ratings_dataset, measures=['RMSE', 'MAE'], cv=5, verbose=True)


    def knnb_evaluation(self):
        # KNN is typically better when less data can be provided
        # The RMSE and MAE are higher than SVD, but fit and test time are extremely low
        algo = KNNBasic()

        # Run 5-fold cross-validation and print results.
        cross_validate(algo, self.ratings_dataset, measures=['RMSE', 'MAE'], cv=5, verbose=True)

    def normal_predictor_evaluation(self):
        # Use the Normal Predictor algorithm
        algo = NormalPredictor()

        # Run 5-fold cross-validation and print results.
        cross_validate(algo, self.ratings_dataset, measures=['RMSE', 'MAE'], cv=5, verbose=True)

if __name__ == '__main__':
    
    evaluator = BookToUserEvaluator()
    evaluator.svd_evaluation()
    evaluator.knnb_evaluation()
    evaluator.normal_predictor_evaluation()