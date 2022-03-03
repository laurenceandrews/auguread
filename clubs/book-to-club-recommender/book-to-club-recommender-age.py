#!/usr/bin/env python
# coding: utf-8

# In[94]:


import pandas as pd
import numpy as np


# In[95]:


club_id_to_query = 5


# In[96]:


# Load data
df_users = pd.read_csv('updated-data-set/clubs_user.csv', encoding = 'latin1')
df_books = pd.read_csv('updated-data-set/clubs_book.csv', encoding = 'latin1')
df_club_users = pd.read_csv('updated-data-set/clubs_club_users.csv')
df_club_books = pd.read_csv('updated-data-set/clubs_club_books.csv')


# In[97]:


# Gets the users from the specified club
df_club_members = pd.DataFrame(df_club_users['user_id'][df_club_users['club_id'] == club_id_to_query])


# In[98]:


# Get average age of each club
df_club_users_ages = pd.merge(df_club_users, df_users, left_on = 'user_id', right_on = 'id')
df_club_users_ages = df_club_users_ages[['club_id', 'user_id', 'age']]
df_club_avg_ages = pd.DataFrame(df_club_users_ages.groupby('club_id')['age'].mean().reset_index(name = 'average_age'))

df_club_avg_ages.head(10)


# In[99]:


# Find the difference in average age between the queried club and all other clubs
queried_club_avg_age = float(df_club_avg_ages['average_age'][df_club_avg_ages['club_id'] == club_id_to_query])
df_club_avg_ages['age_difference'] = pd.DataFrame(abs(df_club_avg_ages['average_age']-queried_club_avg_age))

# Remove the club that is being queried 
df_club_avg_ages.drop(df_club_avg_ages[df_club_avg_ages['club_id'] == club_id_to_query].index, inplace=True)

df_club_avg_ages = df_club_avg_ages.sort_values('age_difference', ascending=True)
df_club_avg_ages.head(10)


# In[100]:


# Find the club(s) with the closest average age to our selected club
df_closest_club_in_age = df_club_avg_ages['club_id'].iloc[0:2]
closest_age_clubs_df = df_closest_club_in_age.reset_index().rename(columns={'club_id':'id'})
df_closest_club_in_age.head()


# In[113]:


# Get favourite books from the above clubs
df_closest_club_books = pd.merge(df_closest_club_in_age, df_club_books, on = 'club_id')

recommended_books = pd.merge(df_closest_club_books, df_books, left_on = 'book_id', right_on = 'id')
recommended_books.drop(['club_id', 'id_x', 'id_y', 'book_id'], axis = 1, inplace=True)
recommended_books

