import os
import sys
import eyed3
from pydub import AudioSegment

# FIXME: Too many args for a function, optimize it
def convert_mp3(artist, song, path, trackNumber,albumName): 
    finalFile = f'{path}/{artist} - {song}.mp3'

    print(f"Converting {artist} - {song} to mp3...")

    mp4_file = AudioSegment.from_file(f"{path}/{artist} - {song}.mp4")
    mp4_file.export(finalFile, format="mp3", bitrate="320k")
    
    if os.path.isfile(finalFile):
        try:
            os.remove(f"{path}/{artist} - {song}.mp4")
        except OSError:
            print("Something went wrong removing the old file" + OSError)
        else:
            print(f"Converted {artist} - {song} to mp3 successfully")
        mp3File = eyed3.load(finalFile)
        mp3File.tag.track_num = trackNumber
        mp3File.tag.artist = artist
        mp3File.tag.title = song
        mp3File.tag.album = albumName
        mp3File.tag.save()
    else:
        sys.exit("Something went wrong locating the converted .mp3 file.")
