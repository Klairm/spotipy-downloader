import os
import sys
from pydub import AudioSegment


def convert_mp3(artist, song, path):
    print(f"Converting {artist} - {song} to mp3...")
    mp4_file = AudioSegment.from_file(f"{path}/{artist} - {song}.mp4")
    mp4_file.export(f'{path}/{artist} - {song}.mp3',
                    format="mp3", bitrate="320k")
    if os.path.isfile(f"{path}/{artist} - {song}.mp3"):
        print(f"Converted {artist} - {song} to mp3 succesfully")
    else:
        sys.exit("Something went wrong locating the converted .mp3 file.")
