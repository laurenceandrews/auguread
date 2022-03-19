
import numpy as np
import pandas as pd
<<<<<<< HEAD:clubs/book-to-user-recommender/book-to-user.py
from sklearn.metrics.pairwise import cosine_similarity 
from surprise import Reader, Dataset, SVD
from surprise.model_selection import train_test_split, cross_validate  
from models import Book, Book_Rating, Users
=======
from clubs.models import Book, Book_Rating, User
from sklearn.metrics.pairwise import cosine_similarity
from surprise import SVD, Dataset, Reader
from surprise.model_selection import cross_validate, train_test_split
>>>>>>> ae35d0d5f45a512fb76b940bc20724dd9d8346a5:clubs/book_to_user_recommender/book_to_user.py


class BookToUserRecommender:
    def __init__(self, user_id):

        # load dataset

        self.df_books = pd.DataFrame(list(Book.objects.all().values()))
<<<<<<< HEAD:clubs/book-to-user-recommender/book-to-user.py
        self.df_users = pd.DataFrame(list(Users.objects.all().values()))
=======
        self.df_users = pd.DataFrame(list(User.objects.all().values()))
>>>>>>> ae35d0d5f45a512fb76b940bc20724dd9d8346a5:clubs/book_to_user_recommender/book_to_user.py
        self.df_ratings = pd.DataFrame(list(Book_Rating.objects.all().values()))

        self.user_index = user_id

        # removing 0-rating from dataframe
        self.df_ratings.drop(self.df_ratings[self.df_ratings['rating'] == 0].index, inplace=True)

        self.set_age_constraint()
        self.set_columns_to_keep()

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
        self.df_users_cleaned = pd.DataFrame(self.df_users[self.df_users['age'] <= 100])

    def set_columns_to_keep(self):
        # columns to keep
        self.df_books_cleaned = pd.DataFrame(self.df_books[['ISBN', 'title', 'author', 'publication_year', 'publisher']])

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
        minVotes = top_20_books['count'].quantile(0.10)  # minimum votes required to be listed in the Top 250
        top_20_books = top_20_books[top_20_books['count'] > minVotes]
        print('minimum votes = ', minVotes)
        print(top_20_books.shape)
        R = top_20_books['mean']  # average for the book (mean) = (Rating)
        v = top_20_books['count']  # number of votes for the book = (votes)
        C = top_20_books['mean'].mean()  # mean vote across all books
        top_20_books['weighted rating'] = (v / (v + minVotes)) * R + (minVotes / (v + minVotes)) * C
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
        m = highest_rated_author['count'].quantile(0.6)  # minimum votes required to be listed in the top
        highest_rated_author = highest_rated_author[highest_rated_author['count'] > m]
        print('minimum votes =', m)
        print(highest_rated_author.shape)
        R = highest_rated_author['mean']  # average for the author (mean) = (Rating)
        v = highest_rated_author['count']  # number of votes for the author = (votes)
        C = highest_rated_author['mean'].mean()  # mean vote across all authors
        highest_rated_author['weighted rating'] = (v / (v + m)) * R + (m / (v + m)) * C
        highest_rated_author = highest_rated_author.sort_values('weighted rating', ascending=False).reset_index(drop=True)

        return highest_rated_author.iloc[:20]

    def get_collaborative_filtering(self):
        # merge ratings and books to get book titles and drop rows for which title is not available

        self.df_books_cleaned.reset_index(level=0, inplace=True)
        self.df_books_cleaned = self.df_books_cleaned.reset_index().rename(columns={'index': 'id'})
        df_books_ratings = pd.merge(self.df_ratings, self.df_books_cleaned, left_on='book_id', right_on='id')

        # get total counts of no. of occurrence of book
        df_books_ratings['count'] = df_books_ratings.groupby('ISBN').transform('count')['user_id']

        # fetch top 100 books based on count
        isbn = df_books_ratings.drop_duplicates('ISBN').sort_values('count', ascending=False).iloc[:100]['ISBN']

        # filter out data as per the ISBN
        df_books_ratings = df_books_ratings[df_books_ratings['ISBN'].isin(isbn)].reset_index(drop=True)
        return df_books_ratings

    def get_user_book_matrix(self):
        # creating a book-user matrix
        df_books_ratings = self.get_collaborative_filtering()
        matrix = df_books_ratings.pivot(index='User-ID', columns='ISBN', values='Book-Rating')
        return matrix

    def get_train_test(self):
        # create train and test set
        df_books_ratings = self.get_collaborative_filtering()
        reader = Reader(rating_scale=(0, 10))
        surprise_data = Dataset.load_from_df(df_books_ratings[['User-ID', 'ISBN', 'Book-Rating']], reader)
        trainset, testset = train_test_split(surprise_data, test_size=0.25)
        return trainset, testset

    def get_cross_validation(self):
        benchmark = []
        # iterate over all algorithms
        for algorithm in [SVD()]:
            # Perform cross validation
            results = cross_validate(algorithm, surprise_data, measures=['RMSE'], cv=3, verbose=False)

        # Get results & append algorithm name
        tmp = pd.DataFrame.from_dict(results).mean(axis=0)
        tmp = tmp.append(pd.Series([str(algorithm).split(' ')[0].split('.')[-1]], index=['Algorithm']))
        benchmark.append(tmp)

        return pd.DataFrame(benchmark).set_index('Algorithm').sort_values('test_rmse')

    def get_svd_algorithm(self):
        trainset = self.get_train_test()[0]
        svd = SVD()
        svd.fit(trainset)
        return svd

    def get_user_prediction(self):
        # get the prediction of book to recommend
        matrix = self.get_user_book_matrix()
        df_books_ratings = self.get_collaborative_filtering()
        index_val = 111
        # get user id

        userId = matrix.index[index_val]
        books = []
        ratings = []
        titles = []

        for isbn in matrix.iloc[index_val][matrix.iloc[index_val].isna()].index:
            books.append(isbn)
            title = df_books_ratings[df_books_ratings['ISBN'] == isbn]['title'].values[0]
            titles.append(title)
            ratings.append(svd.predict(userId, isbn).est)

        prediction = pd.DataFrame({'ISBN': books, 'title': titles, 'rating': ratings, 'userId': userId})
        prediction = prediction.sort_values('rating', ascending=False).iloc[:10].reset_index(drop=True)

        # get other highly rated books by user
        temp = df_books_ratings[df_books_ratings['User-ID'] == matrix.index[index_val]].sort_values(
            'Book-Rating', ascending=False)[['Book-Rating', 'title', 'User-ID']].iloc[:10].reset_index(drop=True)
        prediction['Book Read'] = temp['title']
        prediction['Rated'] = temp['Book-Rating']
        return prediction

    def get_similarity_matrix(self):
        matrix = self.get_user_book_matrix()
        # replace NaN with user based average rating in pivot (matrix) dataframe
        matrix_imputed = matrix.fillna(matrix.mean(axis=0))

        # get similarity between all users
        similarity_matrix = cosine_similarity(matrix_imputed.values)
        return similarity_matrix

    def get_recommendation(self):
        matrix = self.get_user_book_matrix()
        similarity_matrix = self.get_similarity_matrix()
        df_books_ratings = self.get_collaborative_filtering()

        # get the top 10 most popular authors
        idx = self.user_index
        sim_scores = list(enumerate(similarity_matrix[idx]))

        # get books that are unrated by the given user
        unrated_books = matrix.iloc[idx][matrix.iloc[idx].isna()].index

        # get weighted ratings of unrated books by all other users
        book_ratings = (matrix[unrated_books].T * similarity_matrix[idx]).T

        # get top 100 similar users by skipping the current user
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:101]

        # get mean of book ratings by top 100 most similar users for the unrated books
        book_ratings = book_ratings.iloc[[x[0] for x in sim_scores]].mean()

        # get rid of null values and sort it based on ratings
        book_ratings = book_ratings.reset_index().dropna().sort_values(0, ascending=False).iloc[:10]

        # get recommended book titles in sorted order
        recommended_books = df_books_ratings[df_books_ratings['ISBN'].isin(book_ratings['ISBN'])][['ISBN', 'title']]
        recommended_books = recommended_books.drop_duplicates('ISBN').reset_index(drop=True)
        assumed_ratings = book_ratings[0].reset_index(drop=True)

        return pd.DataFrame({'ISBN': recommended_books['ISBN'],
                             'Recommended Book': recommended_books['title'],
                             'Assumed Rating': assumed_ratings})

    def get_recommended_books(self):
        matrix = self.get_user_book_matrix()
        df_books_ratings = self.get_collaborative_filtering()
        recommended_books = self.get_recommendation(user_index)

        user_index = self.user_index

        # get other highly rated books by user
        temp = df_books_ratings[df_books_ratings['User-ID'] == matrix.index[user_index]].sort_values(
            'Book-Rating', ascending=False)[['Book-Rating', 'title', 'User-ID']].iloc[:10].reset_index(drop=True)
        recommended_books['userId'] = temp['User-ID']
        recommended_books['Book Read'] = temp['title']
        recommended_books['Rated'] = temp['Book-Rating']
        return recommended_books
