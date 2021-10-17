import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
import models.Recommenders as Recommenders

conn = sqlite3.connect('MusicPlayer.db')
sql_query = pd.read_sql_query('''SELECT * FROM Interactions''', conn)

rating_df = pd.DataFrame(
    sql_query, columns=['id', 'user_id', 'song_id', 'like', 'listen_count'])
rating_df.drop(labels=['like'], axis=1, inplace=True)
sql_query = pd.read_sql_query('''
                               SELECT
                               *
                               FROM Songs
                               ''', conn)

song_df = pd.DataFrame(sql_query, columns=[
                       'id', 'name', 'path', 'artist', 'genre', 'cover_photo', 'duration', 'total_likes', 'total_listen_count'])

song_df.drop(labels=['path', 'cover_photo', 'duration',
                     'total_likes', 'total_listen_count'], axis=1, inplace=True)
song_df.rename(columns={'id': 'song_id'}, inplace=True)

merged_song_df = pd.merge(rating_df, song_df.drop_duplicates(
    ['song_id']), on="song_id", how="left")
train_data, test_data = train_test_split(
    merged_song_df, test_size=0.20, random_state=0)


def popular_recommender(user_id):
    pm = Recommenders.popularity_recommender_py()
    pm.create(train_data, 'user_id', 'name')
    return pm.recommend(user_id)


ratings_mat = np.ndarray(shape=(np.max(rating_df.song_id.values), np.max(
    rating_df.user_id.values)), dtype=np.uint8)
ratings_mat[rating_df.song_id.values-1,
            rating_df.user_id.values-1] = rating_df.listen_count.values

normalised_mat = ratings_mat - np.asarray([(np.mean(ratings_mat, 1))]).T
A = normalised_mat.T / np.sqrt(ratings_mat.shape[0] - 1)
U, S, V = np.linalg.svd(A)


def top_cosine_similarity(data, movie_id, top_n=18):
    index = movie_id - 1  # Movie id starts from 1 in the dataset
    movie_row = data[index, :]
    magnitude = np.sqrt(np.einsum('ij, ij -> i', data, data))
    similarity = np.dot(movie_row, data.T) / (magnitude[index] * magnitude)
    sort_indexes = np.argsort(-similarity)
    return sort_indexes[:top_n]


def print_similar_songs(song_df, song_id, top_indexes):
    print('Recommendations for {0}: \n'.format(
        song_df[song_df.song_id == song_id].name.values[0]))
    songs = []
    for id in top_indexes + 1:
        songs.append(song_df[song_df.song_id == id].name.values[0])
    return songs


def recommend_songs(song_id):
    k = 50
    song_id = int(song_id)
    top_n = 18
    sliced = V.T[:, :k]  # representative data
    indexes = top_cosine_similarity(sliced, song_id, top_n)
    print(indexes)
    songs = print_similar_songs(song_df, song_id, indexes)
    return songs
