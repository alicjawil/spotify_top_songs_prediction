import urllib
import spotipy
import json
import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials

c_id = "f0b56afe88ec4ec28721cc96eb9fb565"
secret_key = "2ecb61239a474a7aa40a750302b43d26"

def get_songs_by_year_released(client: spotipy.Spotify, year: int) -> pd.DataFrame:
    ''' returns a pandas dataframe of songs of given year

        Parameters:
            - client: spotipy wrapper client
            - year: the year in which songs were released
    '''
    result = []
    for i in range(101):
        search_results = client.search(q="year:2017", market="US", limit=50, offset=50*i)
        for item in search_results.get("tracks").get("items"):
            artist = item.get("artists")[0].get("name")
            track = item.get("name")
            track_id = item.get("id")
            t = {"artist": artist, "track": track, "id": track_id}
            result.append(t)
    return pd.DataFrame(result)

def get_songs_features(client: spotipy.Spotify, df: pd.DataFrame) -> pd.DataFrame:
    ''' returns a pandas dataframe of song features of given songs

        Parameters:
            - client: spotipy wrapper client
            - df: pandas dataframe of songs from get_songs_by_year_released
    '''
    result = []
    songs_id = df["id"]
    for i in range(101):
        features = client.audio_features(songs_id[50*i:50*(i+1)])
        for s in features:
            result.append(s)
    features = pd.DataFrame(result)
    features[["artist", "track"]] = df[["artist", "track"]]
    return features

def get_top_tracks_of_2017(client: spotipy.Spotify, df: pd.DataFrame, playlist_id: str) -> pd.DataFrame:
    ''' returns an updated pandas dataframe of song features with a new hit value:
        0 - not in the given top playlist
        1 - in the given top playlist

        Parameters:
            - client: spotipy wrapper client
            - df: pandas dataframe of song features from get_songs_features
            - playlist_id: public playlist id of the top songs
    '''
    uri = f"spotify:user:spotifycharts:playlist:{playlist_id}"
    username = uri.split(':')[2]
    playlist_id = uri.split(':')[4]
    playlist_results = client.user_playlist(username, playlist_id)
    df["hit"] = 0
    hit_songs = [item.get("track").get("id") for item in playlist_results.get("tracks").get("items")]
    df.loc[df["id"].isin(hit_songs), "hit"] = 1
    return df

if __name__ == '__main__':
    # step 1: create a client
    print("Created client for the Spotify Web API...")
    client = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=c_id, client_secret=secret_key))

    # step 2: scrape for songs released in a given year
    print("Getting songs...")
    songs_2017 = get_songs_by_year_released(client, 2017)

    # step 3: save songs result to csv
    songs_2017.to_csv("songs_2017.csv", encoding="utf-8", index=False)

    # step 4: scrape for features from songs scraped in step 2
    print("Getting features...")
    df_songs_2017 = pd.read_csv("songs_2017.csv")
    songs_2017_features = get_songs_features(client, df_songs_2017)

    # step 5: save feature results to csv
    songs_2017_features.to_csv("features_2017.csv", encoding="utf-8", index=False)

    # step 6: scrape for songs in the top playlist (given playlist_id) and update features
    df_features_2017 = pd.read_csv("features_2017.csv")
    updated_features = get_top_tracks_of_2017(client, df_features_2017, "37i9dQZF1DX5nwnRMcdReF")

    # step 7: save updated feature results to csv
    updated_features.to_csv("updated_features_2017.csv", encoding="utf-8", index=False)

    

