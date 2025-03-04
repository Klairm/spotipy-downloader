import os
import sys
import eyed3
from pydub import AudioSegment

# FIXME: Too many args for a function, optimize it, create a ""record/data class""?
def convert_mp3(artist, song, path,albumName): 
    finalFile = f'{path}/{artist} - {song}.mp3'
    expectedFile = f"{path}/{artist} - {song}.webm"
    print(f"Converting {artist} - {song} to mp3...")

    if os.path.exists(expectedFile):
        
        mp4_file = AudioSegment.from_file(expectedFile)
        mp4_file.export(finalFile, format="mp3", bitrate="320k")
    
    if os.path.isfile(finalFile):
        print(f"Converted {artist} - {song} to mp3 successfully")
        mp3File = eyed3.load(finalFile)
        mp3File.tag.artist = artist
        mp3File.tag.title = song
        mp3File.tag.album = albumName
        mp3File.tag.save()
        print("Added metadata to the song.")
    else:
        sys.exit("Something went wrong locating the converted .mp3 file.")

    
