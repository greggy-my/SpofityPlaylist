import requests
import bs4
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import base64
import os

spotify_id = os.environ['SPOTIFY_CLIENT_ID']
spotify_secret = os.environ['SPOTIFY_CLIENT_SECRET']
print(spotify_id)
print(spotify_secret)
SPOTIFY_REDIRECT_URL = 'http://localhost:8888/callback'

# date = input('What date would we use for a playlist? (yyyy-mm-dd) ')
date = '2001-09-10'
URL_BILLBOARD = f'https://www.billboard.com/charts/hot-100/{date}/'

# Getting billboard html
response = requests.get(url=URL_BILLBOARD)
billboard_html = response.text
soup = bs4.BeautifulSoup(billboard_html, 'html.parser')

# Getting song_data
song_data = {
    'name': [],
    'artist': []
}

titles_raw = [title.find(name='h3', id='title-of-a-story').get_text() for title in
              soup.find_all(name='li', class_="o-chart-results-list__item")
              if title.find(name='h3', id='title-of-a-story') is not None]
artists_raw = [artist.find(name='span').get_text() for artist in
               soup.find_all(name='li', class_="o-chart-results-list__item")
               if artist.find(name='h3', id='title-of-a-story') is not None]

for i in range(len(titles_raw) - 1):
    song_data['name'].append(titles_raw[i].replace('\t', "").replace('\n', ""))
    song_data['artist'].append(artists_raw[i].replace('\t', "").replace('\n', ""))

# Spotify Authorisation
scope = 'playlist-modify-public ugc-image-upload'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=spotify_id,
                                               client_secret=spotify_secret,
                                               redirect_uri=SPOTIFY_REDIRECT_URL,
                                               scope=scope))

# Creating a playlist

user_id = sp.me()['id']
playlist_info = sp.user_playlist_create(user=user_id, name=date)
playlist_id = playlist_info['id']
playlist_name = playlist_info['name']

# Adding tracks to playlist

for index, track_name in enumerate(song_data['name']):
    track_information = sp.search(q=track_name, type='track')
    track_uri = track_information['tracks']['items'][0]['uri']
    sp.playlist_add_items(playlist_id=playlist_id, items=[track_uri], position=index)

# Adding a cover for a playlist

with open("image.jpeg", "rb") as image_file:
    image_b64 = base64.b64encode(image_file.read()).decode()
    sp.playlist_upload_cover_image(playlist_id=playlist_id, image_b64=image_b64)