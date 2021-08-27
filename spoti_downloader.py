import spotipy
import sys
import json
import os
import re
from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch
from pytube import YouTube
import pytube.request
import pytube.extract


# Need to change the chunk size to get on_progress callbacks if the song downloading is lower than 9MB -> https://github.com/pytube/pytube/issues/1017
pytube.request.default_range_size = 1048576  # Changed to 1MB

offset = 0


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
    sys.exit()

if len(sys.argv) <= 1:
    # Path is optional, by default it will be the current one.
    print("Usage: spoti_downloader.py playlist_url/track_url [path]")
    sys.exit()

# https://open.spotify.com/track/0Zk2R0TwYeOpYUePX7Nm6x?si=db1ff381174442de
# https://open.spotify.com/playlist/0K7PkGHxDIUyaLJ0nxqQhn?si=bafc41cff77a4030

data_url = sys.argv[1]
if len(sys.argv) < 3:
    print("Using default path...")
    download_path = "."
else:
    download_path = sys.argv[2]


client_credentials_manager = SpotifyClientCredentials(client_id=cred_json.get(
    'client_id'), client_secret=cred_json.get('client_secret'))
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

if data_url.__contains__('playlist'):
    total = sp.playlist_items(data_url, fields='total').get('total')
else:
    total = 1


def completed(artist, song_name):
    print(f"Downloaded {artist} - {song_name}")


def progress_bar(chunk, _file_handle, bytes_remaining):
    size = songDownload.filesize
    # X/Y * 100 = Z
    print(
        f"Downloading {((size - bytes_remaining) / size) * 100:.0f}% - {artist} - {song_name}", end='\r')
    if bytes_remaining == 0:
        print(f"Download completed {artist} - {song_name}")


while offset < total:
    if offset == total:
        break
    # Get artist name and song name using the spotify API
    if data_url.__contains__('playlist'):
        artist = sp.playlist_items(data_url, offset=offset, fields='items.track.artists.name').get(
            'items')[0].get('track').get('artists')[0].get('name')
        song_name = sp.playlist_items(data_url, offset=offset, fields='items.track.name').get(
            'items')[0].get('track').get('name')
    elif data_url.__contains__('track'):
        artist = sp.track(data_url).get('artists')[0].get('name')
        song_name = sp.track(data_url).get('name')

    offset += 1

    if os.path.exists(f"{download_path}/{artist} - {song_name}.mp4"):
        print(f"Skip existing song... {artist} - {song_name}")
    else:

        yt_link = VideosSearch(f"{artist} {song_name}", limit=1).result().get(
            'result')[0].get('link')
        song_name = re.sub(r'[<>:"/\|?*]', '', song_name)

        # FIXME: Optimize this
        song = YouTube(yt_link)

        while(song.age_restricted):
            print("Restricted age song detected, searching next result...")
            yt_link = VideosSearch(f"{artist} {song_name}", limit=1)
            yt_link.next()
            yt_link = yt_link.result().get(
                'result')[0].get('link')
            song = YouTube(yt_link)

        songDownload = YouTube(
            yt_link, on_progress_callback=progress_bar).streams.get_audio_only()

        songDownload.download(output_path=download_path,
                              filename=f"{artist} - {song_name}.mp4")
