
import numpy as np
import pandas as pd
from clubs.models import Book, Book_Rating, User


class BookToUserRecommender:
    def __init__(self):

        # load datasets

        self.df_books = pd.DataFrame(list(Book.objects.all().values()))
        self.df_users = pd.DataFrame(list(User.objects.all().values()))
        self.df_ratings = pd.DataFrame(list(Book_Rating.objects.all().values()))

        self.df_ratings.drop(self.df_ratings[self.df_ratings['rating'] == 0].index, inplace=True)
        self.df_books = self.df_books.dropna(how='any')
        self.df_ratings = self.df_ratings.dropna(how='any')

    # experimental layout for implementation

    def get_top_books(self):
        # get the top 20 highest rated books
        top_20_books = pd.DataFrame(self.df_ratings.groupby('id').agg(['mean', 'count'])['rating'].reset_index())

        # generate score based on mean rating and total number of times the book is rated
        min_votes = top_20_books['count'].quantile(0.10)  # minimum votes required
        top_20_books = top_20_books[top_20_books['count'] > min_votes]
        print('minimum votes for books = ', min_votes)
        print(top_20_books.shape)
        rating_mean = top_20_books['mean']  # average for the book (mean) = (Rating)
        vote_count = top_20_books['count']  # number of votes for the book = (votes)
        vote_mean = top_20_books['mean'].mean()  # mean vote across all books
        top_20_books['weighted rating'] = ((vote_count / (vote_count + min_votes)) * rating_mean +
                                           (min_votes / (vote_count + min_votes)) * vote_mean)

        top_20_books = top_20_books.sort_values('weighted rating', ascending=False).reset_index(drop=True)

        # get title of books
        top_books_to_recommend = pd.merge(top_20_books, self.df_books, on='id')[['title', 'author', 'mean',
                                                                                 'count', 'weighted rating', 'publication_year']].drop_duplicates('title').iloc[:10]
        # breakpoint()
        print(top_books_to_recommend)
        return top_books_to_recommend

    def get_top_authors(self):
        # top 10 highest rated authors

        # drop any duplicates
        self.df_books = self.df_books.drop_duplicates(['author', 'title'])

        # get book-author and title
        highest_rated_author = pd.merge(self.df_books, self.df_ratings, on='id')[['author', 'rating', 'title', 'id']]
        highest_rated_author = highest_rated_author.groupby('author').agg(['mean', 'count'])['rating'].reset_index()

        # generate score based on mean rating and total number of times the author is rated
        min_votes_author = highest_rated_author['count'].quantile(0.4)  # minimum votes required to be listed in the top
        highest_rated_author = highest_rated_author[highest_rated_author['count'] > min_votes_author]

        print('minimum votes for authors =', min_votes_author)
        print(highest_rated_author.shape)

        rating_mean_author = highest_rated_author['mean']  # average for the author (mean) = (Rating)
        vote_count_author = highest_rated_author['count']  # number of votes for the author = (votes)
        vote_mean_author = highest_rated_author['mean'].mean()  # mean vote across all authors
        highest_rated_author['weighted rating'] = ((vote_count_author / (vote_count_author + min_votes_author)) *
                                                   rating_mean_author + (min_votes_author / (vote_count_author + min_votes_author)) * vote_mean_author)

        highest_rated_author = highest_rated_author.sort_values('weighted rating', ascending=False).reset_index(drop=True)

        authors_to_recommend_list = list(highest_rated_author.iloc[:10])

        # breakpoint()
        print('get_top_authors return list count: ', len(authors_to_recommend_list))

        return authors_to_recommend_list

    def get_collaborative_filtering(self):
        # merge ratings and books to get book titles and drop rows for which title is not available

        df_books_ratings = pd.merge(self.df_ratings, self.df_books, left_on='book_id', right_on='id')

        # get total counts of no. of occurrence of book
        df_books_ratings['count'] = df_books_ratings.groupby('book_id').transform('count')['user_id']

        # fetch top 100 books based on count
        isbn = df_books_ratings.drop_duplicates('book_id').sort_values('count', ascending=False).iloc[:100]['book_id']
        # filter out data as per the ISBN
        df_books_ratings = df_books_ratings[df_books_ratings['book_id'].isin(isbn)].reset_index(drop=True)

        # remove columns
        # df_books_ratings = df_books_ratings.drop(['image_small', "image_medium", "image_large"])

        books_ratings_list = df_books_ratings['book_id'].tolist()

        # breakpoint()
        # print('collaborative filtering output =', df_books_ratings.head(15))
        # print('df shape: ', df_books_ratings.shape)
        # print('get_collaborative_filtering list count: ', len(books_ratings_list))

        return books_ratings_list
