import spotipy
import sys
import json
import os
from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch
from pytube import YouTube


try:
    with open("credentials.json", "r") as credentials:
        cred_json = json.load(credentials)

except FileNotFoundError:

    print('''File credentials.json not found, please create one with the following syntax:
{
    "client_id":"your_client_id_here",
    "client_secret":"your_client_secret_id_here"
}

        ''')

if len(sys.argv) <= 1:
    # Path is optional, by default it will be the current one.
    print("Usage: spoti_downloader.py playlist_url [path]")
    sys.exit()


playlist_url = sys.argv[1]
if len(sys.argv) < 3:
    print("Using default path...")
    download_path = "."
else:
    download_path = sys.argv[2]

offset = 0

client_credentials_manager = SpotifyClientCredentials(client_id=cred_json.get(
    'client_id'), client_secret=cred_json.get('client_secret'))
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

total = sp.playlist_items(playlist_url, fields='total').get('total')


def completed(artist, song_name):
    print(f"Downloaded {artist} - {song_name}")

while offset < total:
    if offset == total:
        break
    artist = sp.playlist_items(playlist_url, offset=offset, fields='items.track.artists.name').get(
        'items')[0].get('track').get('artists')[0].get('name')
    song_name = sp.playlist_items(playlist_url, offset=offset, fields='items.track.name').get(
        'items')[0].get('track').get('name')
    offset += 1
    if os.path.exists(f"{download_path}/{artist} - {song_name}.mp4"):
        print(f"Skip existing song... {artist} - {song_name}")
    else:
        yt_link = VideosSearch(f"{artist} {song_name}", limit=1).result().get('result')[0].get('link')
        song = YouTube(yt_link,on_complete_callback=completed(artist, song_name)).streams.get_audio_only()
        song.download(output_path=download_path, filename=f"{artist} - {song_name}")

