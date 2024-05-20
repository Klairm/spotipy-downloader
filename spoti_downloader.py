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
from util.converter import convert_mp3
from util.util import cleanString

# Need to change the chunk size to get on_progress callbacks if the song downloading is lower than 9MB -> https://github.com/pytube/pytube/issues/1017
pytube.request.default_range_size = 1048576  # Changed to 1MB

offset = 0


class NotEnoughArgs(Exception):
    pass


class InvalidURL(Exception):
    pass


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
except NotEnoughArgs:
    sys.exit()
if len(sys.argv) <= 1:
    # Path is optional, by default it will be the current one.
    raise NotEnoughArgs(
        "Usage: spoti_downloader.py playlist_url/track_url [path]")


data_url = sys.argv[1]

data_url = re.sub("/intl[\D][a-z]*","",data_url) # Remove intl-* from the url to make it valid
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
elif data_url.__contains__('album'):
    total = sp.album_tracks(data_url).get('total')
elif data_url.__contains__('track'):
    total = 1
else:
    raise InvalidURL(
        "The URL of the album/playlist/track seems to be invalid.")

def completed(artist, songName):

    print(f"Downloaded {artist} - {songName}")


def progress_bar(chunk, _file_handle, bytes_remaining):
    size = song.filesize
    # X/Y * 100 = Z
    print(
        f"Downloading {((size - bytes_remaining) / size) * 100:.0f}% - {artistName} - {songName}", end='\r')
    if bytes_remaining == 0:
        print(f"Download completed {artistName} - {songName}")


def getTrackData(offset):
    # Get artist name and song name using the spotify API
    artistName = ''
    songName = ''
    albumName = ''

    if data_url.__contains__('playlist'):
        artistName = sp.playlist_items(data_url, offset=offset, fields='items.track.artists.name').get(
            'items')[0].get('track').get('artists')[0].get('name')
        songName = sp.playlist_items(data_url, offset=offset, fields='items.track.name').get(
            'items')[0].get('track').get('name')
        albumName = sp.playlist(data_url,fields='name').get('name')        

    elif data_url.__contains__('album'):
        artistName = sp.album_tracks(data_url, offset=offset).get('items')[
            0].get('artists')[0].get('name')
        songName = sp.album_tracks(data_url, offset=offset).get('items')[
            0].get('name')
        albumName = sp.album(data_url).get('name')

    elif data_url.__contains__('track'):
        artistName = sp.track(data_url).get('artists')[0].get('name')
        songName = sp.track(data_url).get('name')
        albumName = sp.track(data_url).get('album').get('name')


    return  cleanString(songName),cleanString(artistName) ,cleanString(albumName)

def downloadTrack(artistName, songName):
    
    if os.path.exists(f"{download_path}/{artistName} - {songName}.mp3"):
        print(f"Skip existing song... {artistName} - {songName}")
    else:

        yt_link = VideosSearch(f"{artistName} {songName}", limit=1).result().get(
            'result')[0].get('link')

        # FIXME: Optimize this
        global song 

        song = YouTube(yt_link,on_progress_callback=progress_bar)

        while song.age_restricted:
            print("Restricted age song detected, searching next result...")
            yt_link = VideosSearch(f"{artistName} {songName}", limit=1)
            yt_link.next()
            yt_link = yt_link.result().get(
                'result')[0].get('link')
            song = YouTube(yt_link)




        song = song.streams.get_audio_only('mp4')
        song.download(output_path=download_path,filename=f"{artistName} - {songName}.mp4")



while offset < total:
    if offset == total:
        break
    artistName, songName ,albumName = getTrackData(offset)

    downloadTrack(artistName, songName)

    convert_mp3(artistName, songName, download_path,offset+1,albumName)
    offset += 1
