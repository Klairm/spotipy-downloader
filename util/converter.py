import os
import sys
import subprocess
import eyed3


# FIXME: Too many args for a function, optimize it, create a ""record/data class""?

def convert_mp3(artist, song, path,albumName): 
    expectedFile = f'{path}/{artist} - {song}.webm'
    finalFile = f'{path}/{artist} - {song}.mp3'

    
    if os.path.isfile(expectedFile):

         

        # Run FFmpeg to convert to MP3
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', expectedFile,  # Input file
            '-vn',  # No video
            '-ar', '44100',  # Set sample rate
            '-ac', '2',  # Stereo audio
            '-b:a', '192k',  # Set bitrate
            '-y',
            finalFile  # Output file
        ]
        subprocess.run(ffmpeg_cmd)
        print("Song converted")
        mp3File = eyed3.load(finalFile)
        print(mp3File)
        mp3File.tag.artist = artist
        mp3File.tag.title = song
        mp3File.tag.album = albumName
        mp3File.tag.save()
        print("Added metadata to the song.")
    else:
        sys.exit("Something went wrong locating the .mp3 file.")

    
