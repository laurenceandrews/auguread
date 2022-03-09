#!/usr/bin/env python
# coding: utf-8

# In[209]:


import pandas as pd
import numpy as np


# In[210]:


club_id_to_query = 10


# In[211]:


# Load data
df_club_users = pd.read_csv('updated-data-set/clubs_club_users.csv')
df_club_books = pd.read_csv('updated-data-set/clubs_club_books.csv')
df_books = pd.read_csv('updated-data-set/clubs_book.csv', encoding = 'latin1')
df_book_ratings = pd.read_csv('BX-Book-Ratings.csv', encoding = 'latin1', sep = ';')


# In[212]:


# Get id of all rows with a book rating of 0
df_book_ratings.drop(df_book_ratings[df_book_ratings['Book-Rating'] == 0].index, inplace = True)


# In[213]:


# Find the number of ratings made by each user
df_rating_count = pd.DataFrame(df_book_ratings.groupby('User-ID')['Book-Rating'].count())

# Make Rating count as a regular column
df_rating_count.reset_index(level=0, inplace=True)

# Remove from the ratings table, all users with less than 20 ratings
df_rating_count.drop(df_rating_count[df_rating_count['Book-Rating'] < 20].index, inplace = True)
df_rating_count.drop('Book-Rating', axis = 1, inplace=True)

df_book_ratings = pd.merge(df_book_ratings, df_rating_count, on = 'User-ID')
df_book_ratings


# In[214]:


# Get the favourite books of the club specified
df_favourite_books = pd.DataFrame(df_club_books['book_id'][df_club_books['club_id'] == club_id_to_query])
df_favourite_books


# In[215]:


# Get ISBNs of the club's favourite books
df_favourite_books = pd.merge(df_favourite_books, df_books, left_on = 'book_id', right_on = 'id')

# Get ISBNs and authors of the favourite books
fav_authors = df_favourite_books['author'].tolist()
fav_books_ISBNs = df_favourite_books['ISBN'].tolist()
df_favourite_books.head(5)


# In[216]:


# Get all books by the favourite authors
df_all_author_books = pd.DataFrame()

for author in fav_authors:
    df_author_books = pd.DataFrame(df_books['ISBN'][df_books['author'] == author])
    # Exclude the books that are from the club's favourite books
    df_author_books = df_author_books[~df_author_books.ISBN.isin(df_favourite_books.ISBN)]
    df_all_author_books = pd.concat([df_all_author_books, df_author_books])

df_all_author_books.head(10)


# In[217]:


# Get the most rated books from the above list
df_author_book_ratings = pd.merge(df_all_author_books, df_book_ratings, on = 'ISBN')
df_author_books_rating_count = pd.DataFrame(df_author_book_ratings.groupby('ISBN')['Book-Rating'].count())

# Make Rating count as a regular column and sort
df_author_books_rating_count.reset_index(level=0, inplace=True)
df_author_books_rating_count.sort_values('Book-Rating', ascending = False)

recommended_books = df_author_books_rating_count['ISBN'].iloc[0:10]
recommended_books = pd.merge(recommended_books, df_books, on = 'ISBN')

