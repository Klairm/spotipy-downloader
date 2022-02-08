## Spotipy Downloader

Little script in Python to download spotify playlists and tracks.

## Requirements

All the requirements are listed in the requirements.txt, use `python3 -m pip install -r requirements.txt` to install them.

## Syntax:

```
	python3 spoti_downloader.py [playlist_url or track_url] (download_path)

```

## Options

| Option                      | Description                                                           | Example                                                                                                 |
| --------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `download_path`             | (Optional) Set the download path where to download the track/playlist | `python3 spoti_downloader.py URL /home/user/Music/Rock/`                                                |
| `playlist_url or track_url` | The track or playlist you want to download                            | `python3 spoti_downloader.py https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT?si=a7d18990986c4f12` |

## Credentials

Credentials are needed in a separate file named `credentials.json` following this structure:

```
{
    "client_id":"your_client_id_here",
    "client_secret":"your_client_secret_id_here"
}
```

If you don't know how to get the client_id and client_secret, you must do the following:

```
    1. Browse to https://developer.spotify.com/dashboard/applications.

    2. Log in with your Spotify account.

    3. Click on ‘Create an app’.

    4. Pick an ‘App name’ and ‘App description’ of your choice and mark the checkboxes.

    After creation, you see your ‘Client Id’ and you can click on ‘Show client secret` to unhide your ’Client secret’.
```

## Credits (Modules used):

    	- Spotipy https://github.com/plamere/spotipy
    	- youtube-search-python https://github.com/alexmercerind/youtube-search-python
    	- Pytubee https://github.com/pytube/pytube
        - Pydub https://github.com/jiaaro/pydub

### Dependencies

    FFmpeg - https://www.ffmpeg.org/download.html

