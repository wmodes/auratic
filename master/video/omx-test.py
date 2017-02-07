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

def playMedia(filename="demo.mp4", duration=0, position=0):
    """ contributed version that turns on and off player (not seamless"""
    player = OMXPlayer(filename)
    player.set_aspect_mode("fill")
    if position > 0:
            player.set_position(position)
    player.duration() # this only works if this line is here
    if duration == 0:
            duration = player.duration() - position
    player.play()
    sleep(duration)
    player.quit()
    return True

def play_film(player, filename="demo.mp4", position=0, duration=0):
    trim_from_end = 0.25
    player.load(filename)
    # check and set position
    full_length = player.duration()
    if position > 0 and position < full_length:
        player.set_position(position)
    else:
        position = 0
    # check and set duration
    our_length = player.duration()
    if duration == 0 or duration > our_length:
        duration = our_length - trim_from_end
    player.play()
    print "full length:", full_length
    print "pos:", position, 
    print "our length:", our_length
    print "duration:", duration
    sleep(duration)
    player.pause()
    print "post sleep pos:", player.position()
    return True

def play_wait(player):
    old_pos = -1
    while (player.position() != old_pos):
        print "status:", player.playback_status(),
        print "old_pos:", old_pos,
        old_pos =  player.position()
        print "new_pos:", old_pos
        sleep(0.001)

def main():
    # This will start an omxplayer process, this might
    # fail the first time you run it, currently in the
    # process of fixing this though.
    rotate_count = 0
    #while True:

        #rotate_count += 1
        #if rotate_count > len(rotate_films)):
            #rotate_count = 0

    try:
        player = OMXPlayer(choice(trans_films))
        #player.set_aspect_mode("fill")

        player = OMXPlayer(choice(trans_films))

        play_film(player, filename=choice(trans_films), duration=1)
        play_film(player, filename=choice(rotate_films))
        play_film(player, filename=choice(trans_films), duration=1)
        play_film(player, filename=choice(rotate_films))
        print "Done."

        #player.load(choice(rotate_films))
        #player.play_sync()
        #player.load(choice(trans_films))
        #player.play_sync()
        #player.load(choice(rotate_films))
        #player.play_sync()
        #player.load(choice(trans_films))
        #player.play_sync()
        # Kill the `omxplayer` process gracefully.
        player.quit()
    except KeyboardInterrupt:
        # Kill the `omxplayer` process gracefully.
        player.quit()

if __name__ == "__main__":
    main()
