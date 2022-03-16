#!/usr/bin/env python
# coding: utf-8
# converted from a Jupyter notebook

import numpy as np # linear algebra (not needed)
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import scipy.sparse.linalg as spla # (not used)
from fuzzywuzzy import fuzz
from fuzzywuzzy import process #(not used)
from clubs.models import User, Club, Club_Users, Club_Books

pd.options.mode.chained_assignment = None  # default='warn'

# Junction tables must be filled when new user signed up!
path = './clubs/club-to-user-recommender/'
book_df = pd.read_csv(path + 'clubs_book.csv', encoding = 'Latin1', sep = ',', delimiter=None, index_col=0)
user_df = pd.read_csv(path + 'clubs_user.csv', encoding = 'Latin1', sep = ',')
club_df = pd.read_csv(path + 'clubs_club.csv', encoding = 'Latin1', sep = ',')
club_book_df = pd.read_csv(path + 'clubs_club_books.csv', encoding = 'Latin1', sep = ',')
club_user_df = pd.read_csv(path + 'clubs_club_users.csv', encoding = 'Latin1', sep = ',')
user_book_df = pd.read_csv(path + 'clubs_user_books.csv', encoding = 'Latin1', sep = ',')

# Merge club_user junction table with user table to get ages of all users
def get_user_age_df():
    club_user_age_df = club_user_df.merge(user_df, left_on = 'user_id', right_on = 'id')
    club_user_age_df = club_user_age_df[['id_x', 'club_id', 'user_id', 'age']]
    club_user_age_df = club_user_age_df.rename(columns={'id_x':'club_user_id'}).sort_values('club_user_id', ascending=True)
    return club_user_age_df
# -- comment the return statment and uncomment the next 2 lines to test whether it returns the correct DataFrame
    #print(club_user_age_df)
#get_user_age_df()



# Merge club_user junction table with club table to get locations of all clubs
def get_club_locations_df():
    club_user_location_df = club_user_df.merge(club_df, left_on = 'club_id', right_on = 'id')
    club_user_location_df = club_user_location_df[['id_x', 'club_id', 'user_id', 'location']]
    club_user_location_df = club_user_location_df.rename(columns={'id_x':'club_user_id'}).sort_values('club_user_id', ascending=True)
    return club_user_location_df
# -- comment the return statment and uncomment the next 2 lines to test whether it returns the correct DataFrame
#     print(club_user_location_df)
# get_club_locations_df()


# Merge the club_user_age and club_user_location tables to have all in one table
def merge_age_and_location():
    club_user_age_location_df = get_user_age_df().merge(get_club_locations_df(), left_on = 'club_user_id', right_on = 'club_user_id')
    club_user_age_location_df = club_user_age_location_df[['club_user_id', 'club_id_x', 'user_id_x', 'age', 'location']]
    club_user_age_location_df = club_user_age_location_df.rename(columns={'user_id_x':'user_id', 'club_id_x':'club_id'})
    return club_user_age_location_df
# -- comment the return statment and uncomment the next 2 lines to test whether it returns the correct DataFrame
#     print(club_user_age_location_df)
# merge_age_and_location()


# Get location and average age of each club
def get_average_club_age():
    average_club_age_df = pd.merge(get_user_age_df(), club_df, left_on='club_id', right_on='id').groupby(['club_id', 'name', 'location'])['age'].mean().reset_index(name = 'average_age')
    return average_club_age_df
# -- comment the return statment and uncomment the next 2 lines to test whether it returns the correct DataFrame
#     print(average_club_age_df)
# get_average_club_age()

# Add column for age difference and return clubs in ascending order of difference from my age
def get_age_difference_df():
    my_age = User.objects.alias('age')
    average_club_age_df = get_average_club_age()
    average_club_age_df['age_difference'] = pd.DataFrame(abs(average_club_age_df['average_age'] - my_age))
    average_club_age_difference_df = average_club_age_df.sort_values('age_difference', ascending=True)
    # return average_club_age_difference_df
# -- comment the return statment and uncomment the next 2 lines to test whether it returns the correct DataFrame
    print(average_club_age_difference_df)
get_age_difference_df()

# Return top 10 closest aged club IDs
def get_top_10_by_closest_age():
    average_club_age_difference_df = get_age_difference_df()
    closest_age_clubs_df = average_club_age_difference_df['club_id'].iloc[0:5]
    return closest_age_clubs_df
# -- comment the return statment and uncomment the next 2 lines to test whether it returns the correct DataFrame
#     print(closest_age_clubs_df)
# get_top_10_by_closest_age()


# Merge closest aged club IDs with clubs CSV to get all details
def get_closest_age_clubs_df():
    closest_age_clubs_df = get_top_10_by_closest_age().reset_index().rename(columns={'club_id':'id'})
    closest_age_clubs_df = pd.merge(get_top_10_by_closest_age(), club_df, left_on = 'club_id', right_on = 'id')
    return closest_age_clubs_df
# -- comment the return statment and uncomment the next 2 lines to test whether it returns the correct DataFrame
#     print(closest_age_clubs_df)
# get_closest_age_clubs_df()


# Get user count of each club
def get_user_count_per_club():
    club_user_count_df = pd.merge(get_user_age_df(), club_df, left_on='club_id', right_on='id').groupby(['club_id', 'name'])['user_id'].count().reset_index(name = 'user_count')
    return club_user_count_df
# -- comment the return statment and uncomment the next 2 lines to test whether it returns the correct DataFrame
#     print(club_user_count_df)
# get_user_count_per_club()


# Return clubs with matching location (exact)
def get_clubs_with_exact_location():
    my_location = 'Adelaide, Australia'

    location_match = club_df['location'] == my_location
    closest_location_clubs_df = club_df[location_match]
    return closest_location_clubs_df
# -- comment the return statment and uncomment the next 2 lines to test whether it returns the correct DataFrame
#     print(closest_location_clubs_df)
# get_clubs_with_exact_location()


# need to figure out how to get my_location
# def get_ratio(row):
#     club_location = row['location']
#     my_location = 'Adelaide, Australia'
#     return fuzz.token_sort_ratio(club_location, my_location)

# Return clubs with matching location (using fuzzy search)
def get_clubs_with_matching_loc_fuzzy(row):
    club_location = row['location']
    my_location = 'Adelaide, Australia'
    ratio = fuzz.token_sort_ratio(club_location, my_location)

    my_location = 'AdelAustralia'
    closest_club_location_fuzzy_df = club_df[club_df.apply(ratio, axis=1) > 80]
    closest_club_location_fuzzy_df['location_fuzzy_score'] = club_df.apply(ratio, axis=1)
    closest_club_location_fuzzy_df = closest_club_location_fuzzy_df.sort_values('location_fuzzy_score', ascending=False)

    return closest_club_location_fuzzy_df
# -- comment the return statment and uncomment the next 2 lines to test whether it returns the correct DataFrame
    #print(closest_club_location_fuzzy_df)




# Perform a many-to-many merge to get the favourite books of each club
def get_club_favourite_books():
    club_favourite_books_df = pd.merge(pd.merge(club_df, club_book_df, left_on='id', right_on='club_id'),
                        pd.merge(book_df, club_book_df, left_on='id', right_on='book_id'), on='book_id', how = 'inner') \
                        .groupby(['club_id_x', 'name', 'ISBN'])['title', 'author'].agg(list).reset_index()

    club_favourite_books_df = club_favourite_books_df.rename(columns={'club_id_x':'club_id'})

    club_favourite_books_df['title'] = club_favourite_books_df['title'].str[0]
    club_favourite_books_df['author'] = club_favourite_books_df['author'].str[0]

    return club_favourite_books_df

# Perform a many-to-many merge to get the favourite books of each user
def get_user_favourite_books():
    user_favourite_books_df = pd.merge(pd.merge(user_df, user_book_df, left_on='id', right_on='user_id'),
                        pd.merge(book_df, user_book_df, left_on='id', right_on='book_id'), on='book_id', how = 'inner') \
                            .groupby(['user_id_x', 'first_name','last_name', 'ISBN', 'title', 'author'])['title', 'author'].agg(list).reset_index()

    user_favourite_books_df = user_favourite_books_df.rename(columns={'user_id_x':'user_id'}).drop(0, 1)
    return user_favourite_books_df

# Get the favourite books and authors of one user (me)
def get_fav_books_and_authors_per_user():
    my_id = 142448
    user_favourite_books_df = get_user_favourite_books()
    my_favourite_books_df = user_favourite_books_df.loc[user_favourite_books_df['user_id'] == my_id]
    return my_favourite_books_df

# Get the favourite books and authors of one club
def get_fav_books_and_authors_per_club():
    club_id = 1
    club_favourite_books_df = get_club_favourite_books()
    single_club_favourite_books_df = club_favourite_books_df.loc[club_favourite_books_df['club_id'] == club_id]
    return single_club_favourite_books_df

# Return all matching favourite books between a single user and multiple clubs (using fuzzy search)

# def get_ratio(row):
#     book_title = row['title']
#     return fuzz.token_sort_ratio(book_title, my_favourite_book)

def get_all_favourite_book_matches_fuzzy(row):
    book_title = row['title']
    ratio = fuzz.token_sort_ratio(book_title, my_favourite_book)
    club_favourite_books_df = get_club_favourite_books()

    my_favourite_book = get_fav_books_and_authors_per_user().iloc[0]['title']
    book_0_matches_df = club_favourite_books_df[club_favourite_books_df.apply(ratio, axis=1) > 80]
    book_0_matches_df['book_fuzzy_match_score'] = club_favourite_books_df.apply(ratio, axis=1)

    my_favourite_book = get_fav_books_and_authors_per_user().iloc[1]['title']
    book_1_matches_df = club_favourite_books_df[club_favourite_books_df.apply(ratio, axis=1) > 80]
    book_1_matches_df['book_fuzzy_match_score'] = club_favourite_books_df.apply(ratio, axis=1)

    my_favourite_book = get_fav_books_and_authors_per_user().iloc[2]['title']
    book_2_matches_df = club_favourite_books_df[club_favourite_books_df.apply(ratio, axis=1) > 80]
    book_2_matches_df['book_fuzzy_match_score'] = club_favourite_books_df.apply(ratio, axis=1)

    my_favourite_book = get_fav_books_and_authors_per_user().iloc[3]['title']
    book_3_matches_df = club_favourite_books_df[club_favourite_books_df.apply(ratio, axis=1) > 80]
    book_3_matches_df['book_fuzzy_match_score'] = club_favourite_books_df.apply(ratio, axis=1)

    my_favourite_book = get_fav_books_and_authors_per_user().iloc[4]['title']
    book_4_matches_df = club_favourite_books_df[club_favourite_books_df.apply(ratio, axis=1) > 80]
    book_4_matches_df['book_fuzzy_match_score'] = club_favourite_books_df.apply(ratio, axis=1)

    all_book_matches_df = pd.concat([book_0_matches_df, book_1_matches_df, book_2_matches_df, book_3_matches_df, book_4_matches_df])
    all_book_matches_df = all_book_matches_df.sort_values('book_fuzzy_match_score', ascending=False).dropna(how='any',axis=0)

    return all_book_matches_df

# Return a list of clubs in order of which have the most matching favourite books with the user
def get_average_book_match_df():
    club_average_book_match_df = get_all_favourite_book_matches_fuzzy().groupby(['club_id', 'name'])['book_fuzzy_match_score'].count().reset_index(name = 'book_match_count').sort_values('book_match_count', ascending=False).rename(columns={'name':'club_book_name'})

    return club_average_book_match_df

# Return all matching favourite authors between a single user and multiple clubs (using fuzzy search)
# This works by checking the authors of all of a club's favourite books agains the authors of all of a user's favourite books

# def get_ratio(row):
#     book_author = row['author']
#     return fuzz.token_sort_ratio(book_author, my_favourite_author)

def get_all_favourite_author_matches_fuzzy(row):
    club_favourite_books_df = get_club_favourite_books()
    book_author = row['author']
    ratio = fuzz.token_sort_ratio(book_author, my_favourite_author)

    my_favourite_author = get_fav_books_and_authors_per_user().iloc[0]['author']
    author_0_matches_df = club_favourite_books_df[club_favourite_books_df.apply(ratio, axis=1) > 80]
    author_0_matches_df['author_fuzzy_match_score'] = club_favourite_books_df.apply(ratio, axis=1)

    my_favourite_author = get_fav_books_and_authors_per_user().iloc[1]['author']
    author_1_matches_df = club_favourite_books_df[club_favourite_books_df.apply(ratio, axis=1) > 80]
    author_1_matches_df['author_fuzzy_match_score'] = club_favourite_books_df.apply(ratio, axis=1)

    my_favourite_author = get_fav_books_and_authors_per_user().iloc[2]['author']
    author_2_matches_df = club_favourite_books_df[club_favourite_books_df.apply(ratio, axis=1) > 80]
    author_2_matches_df['author_fuzzy_match_score'] = club_favourite_books_df.apply(ratio, axis=1)

    my_favourite_author = get_fav_books_and_authors_per_user().iloc[3]['author']
    author_3_matches_df = club_favourite_books_df[club_favourite_books_df.apply(ratio, axis=1) > 80]
    author_3_matches_df['author_fuzzy_match_score'] = club_favourite_books_df.apply(ratio, axis=1)

    my_favourite_author = get_fav_books_and_authors_per_user().iloc[4]['author']
    author_4_matches_df = club_favourite_books_df[club_favourite_books_df.apply(ratio, axis=1) > 80]
    author_4_matches_df['author_fuzzy_match_score'] = club_favourite_books_df.apply(ratio, axis=1)

    all_author_matches_df = pd.concat([author_0_matches_df, author_1_matches_df, author_2_matches_df, author_3_matches_df, author_4_matches_df])
    all_author_matches_df = all_author_matches_df.sort_values('author_fuzzy_match_score', ascending=False).dropna(how='any',axis=0)
    return all_author_matches_df

# Return a list of clubs in order of which have the most matching favourite authors with the user

def get_club_average_author_match_df():
    club_average_author_match_df = get_all_favourite_author_matches_fuzzy().groupby(['club_id', 'name'])['author_fuzzy_match_score'].count().unstack(fill_value=0).stack().reset_index(name = 'author_match_count').sort_values('author_match_count', ascending=False).rename(columns={'name':'club_author_name'})
    return club_average_author_match_df

# Get all columns into one dataframe

# Location: average_club_age_difference_df
# Age difference: average_club_age_difference_df
# User count: club_user_count_df
# Favourite books: club_average_book_match_df
# Favourite authors: club_average_author_match_df
def get_best_clubs_df():
    best_clubs_df = get_user_count_per_club().merge(get_age_difference_df(), how = 'left', left_on = 'club_id', right_on = 'club_id')
    best_clubs_df = best_clubs_df.merge(get_average_book_match_df(), how = 'left', left_on = 'club_id', right_on = 'club_id')
    best_clubs_df = best_clubs_df.merge(get_club_average_author_match_df(), how = 'left', left_on = 'club_id', right_on = 'club_id')

    best_clubs_df = best_clubs_df[['club_id', 'club_author_name', 'location', 'age_difference', 'user_count', 'book_match_count', 'author_match_count']]
    best_clubs_df = best_clubs_df.rename(columns={'club_author_name':'club_name'})

    best_clubs_df['book_match_count'] = best_clubs_df['book_match_count'].fillna(0)
    best_clubs_df['author_match_count'] = best_clubs_df['author_match_count'].fillna(0)

    # Dirty way of getting name back...
    best_clubs_df = best_clubs_df.merge(get_age_difference_df(), on = 'club_id')
    best_clubs_df = best_clubs_df[['club_id', 'name', 'location_x', 'age_difference_y', 'user_count', 'book_match_count', 'author_match_count']]
    best_clubs_df = best_clubs_df.rename(columns={'location_x':'location', 'age_difference_y':'age_difference'}, )

    return best_clubs_df


# <h3><b>To do</b></h3>
# <p>Implement algorithm which recommends 10 clubs based on user count, average age, location,
# favourite books and favourite authors</p>
# <br>
# <b>Weighting if online only checkbox checked:</b>
# <ul>
# <li>Favourite books 0.3</li>
# <li>Favourite authors 0.3</li>
# <li>User count: 0.2</li>
# <li>Average age: 0.1</li>
# <li>Location 0.1</li>
# </ul>
# <br>
# <b>Weighting if online only checkbox <i>un</i>checked:</b>
# <ul>
# <li>Location 0.4</li>
# <li>Favourite books 0.2</li>
# <li>Favourite authors 0.2</li>
# <li>User count: 0.1</li>
# <li>Average age: 0.1</li>
# </ul>

# Order if location matters

# TO DO: Find a way to convert location to distance
def get_best_clubs_in_person():
    best_clubs_df = get_best_clubs_df().sort_values(["location_fuzzy_score", "book_match_count", "author_match_count", "age_difference", "user_count"], ascending = [False, False, False, True, False])
    return best_clubs_df
    # print(best_clubs_df)

# Order if online only
def get_best_clubs_online():
    best_clubs_df = get_best_clubs_df().sort_values(["book_match_count", "author_match_count", "age_difference", "user_count"], ascending = [False, False, True, False])
    return best_clubs_df

# get_best_clubs_in_person()
