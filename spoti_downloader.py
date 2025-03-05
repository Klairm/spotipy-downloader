import spotipy
import sys
import json
import os
import re
import time
import yt_dlp
from spotipy.oauth2 import SpotifyClientCredentials
from pytube import YouTube
import pytube.request
import pytube.extract
from util.converter import convert_mp3
from util.util import cleanString
from pydub import AudioSegment
import glob
from concurrent.futures import ThreadPoolExecutor

# Set the range size for pytube
pytube.request.default_range_size = 1048576  # Changed to 1MB

offset = 0
max_threads = os.cpu_count()   # Adjust the number of threads based on your system's capability

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

if len(sys.argv) <= 1:
    raise NotEnoughArgs("Usage: spoti_downloader.py playlist_url/track_url [path]")

data_url = sys.argv[1]
data_url = re.sub("/intl[\D][a-z]*", "", data_url)  # Remove intl-* from the URL to make it valid

if len(sys.argv) < 3:
    print("Using default path...")
    download_path = "."
else:
    download_path = sys.argv[2]

client_credentials_manager = SpotifyClientCredentials(
    client_id=cred_json.get('client_id'), client_secret=cred_json.get('client_secret')
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Determine the total number of tracks to download
if 'playlist' in data_url:
    total = sp.playlist_items(data_url, fields='total').get('total')
elif 'album' in data_url:
    total = sp.album_tracks(data_url).get('total')
elif 'track' in data_url:
    total = 1
else:
    raise InvalidURL("The URL of the album/playlist/track seems to be invalid.")

def completed(artist, songName):
    print(f"Downloaded {artist} - {songName}")


def getTrackData(offset):
    artistName = ''
    songName = ''
    albumName = ''

    if 'playlist' in data_url:
        artistName = sp.playlist_items(data_url, offset=offset, fields='items.track.artists.name').get('items')[0].get('track').get('artists')[0].get('name')
        songName = sp.playlist_items(data_url, offset=offset, fields='items.track.name').get('items')[0].get('track').get('name')
        albumName = sp.playlist_items(data_url, offset=offset, fields='items.track.album.name').get('items')[0].get('track').get('album').get('name')
    elif 'album' in data_url:
        artistName = sp.album_tracks(data_url, offset=offset).get('items')[0].get('artists')[0].get('name')
        songName = sp.album_tracks(data_url, offset=offset).get('items')[0].get('name')
        albumName = sp.album(data_url).get('name')
    elif 'track' in data_url:
        artistName = sp.track(data_url).get('artists')[0].get('name')
        songName = sp.track(data_url).get('name')
        albumName = sp.track(data_url).get('album').get('name')


   
    return cleanString(artistName), cleanString(songName), cleanString(albumName)

def search_video(query):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f"ytsearch:{query}", download=False)
        if 'entries' in result:
            return result['entries'][0]['url']
        return None

def downloadTrack(artistName, songName):

    pattern = os.path.join(download_path, f"{artistName} - {songName}.*")


    if glob.glob(pattern):
        print(f"Skipping existing track... {artistName} - {songName}")
    else:
        yt_link = search_video(f"{artistName} {songName}")
        
        if yt_link is None:
            print(f"Video not found for {artistName} - {songName}")
            return

        print(f"Found video: {yt_link}")

        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            'force-ipv4': True,
            'no-check-certificate': True,
            'format': 'bestaudio/best',
            'outtmpl': f'{download_path}/{artistName} - {songName}.webm',
            'retries': 3,

            
        }

        retry_count = 2
        while retry_count > 0:
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([yt_link])
                    print(f"Downloaded: {artistName} - {songName}")
                    artistName, songName, albumName = getTrackData(offset)
                    convert_mp3(artistName,songName,download_path,albumName)
                    
                   
                    break
            except Exception as e:
                print(f"Error downloading {artistName} - {songName}: {e} ")
                retry_count -= 1
                time.sleep(1200)

def main():
    with ThreadPoolExecutor(max_threads) as executor:
        futures = []
        for offset in range(total):
            artistName, songName, albumName = getTrackData(offset)
            futures.append(executor.submit(downloadTrack, artistName, songName))
            
        for future in futures:
            future.result()  # Wait for all tasks to complete

if __name__ == '__main__':
    main()
