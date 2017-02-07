from omxplayer import OMXPlayer
from time import sleep
from random import choice

file_path_or_url = 'small.mp4'

trans_films = [
        "tv-color-bars-distorted.mp4",
        "tv-color-bars.mp4",
        "tv-color-calibration.mp4",
        "tv-static-transition.mp4",
        "tv-static-transition2.mp4"
        ]

rotate_films = [
        "1960s Cuba, Family Life in East Havana New Developments, Colour Footage.mp4",
        "1960s FAmily films 2 - 1960s Uncle Howie house.mp4",
        "1960s Family Movie.mp4",
        "1960s Suburban Family LIfe, 16mm Colour Home Movies.mp4",
        "1960s Super 8 Film Home Movie - Family Vacation in the Keys.mp4",
        "1960s USA, Baltimore, Family Road Trip, Home Movies.mp4"
        ]

# This will start an `omxplayer` process, this might
# fail the first time you run it, currently in the
# process of fixing this though.
rotate_count = 0
#while True:

    #rotate_count += 1
    #if rotate_count > len(rotate_films)):
        #rotate_count = 0

player = OMXPlayer(choice(rotate_films))

# The player will initially be paused

player.playsync()
player.load(choice(trans_films))
player.playsync()
player.load(choice(rotate_films))
player.playsync()

# Kill the `omxplayer` process gracefully.
player.quit()
