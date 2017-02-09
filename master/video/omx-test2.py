from omxplayer import OMXPlayer
from time import sleep
from random import choice 
file_path_or_url = 'small.mp4'

DEBUG = True

trans_films = [
        "tv-color-bars-distorted.mp4",
        "tv-color-bars.mp4",
        "tv-color-calibration.mp4",
        #"tv-static-transition.mp4",
        "tv-static-transition2.mp4"
        ]

rotate_films = [
        "1960s-baltimore-family.mp4",
        "1960s-cuba-family.mp4",
        "1960s-family-movie.mp4",
        "1960s-family-vacation-keys.mp4",
        "1960s-suburban-family.mp4",
        "1960s-uncle-howie-house.mp4"
        ]


def debug(*args):
    if (DEBUG):
        text = " ".join(list(map(str, args)))
        print text


def play_film(player, filename="demo.mp4", duration=0, position=0):
    debug("\nfilename:", filename)
    debug("  position:", position)
    debug("  duration:", duration)
    trim_from_end = 0.5
    #trim_from_end = 0
    player.load(filename)
    player.set_position(0.0)
    debug("  pre-play pos:", player.position())
    player.play()
    # check and set position
    full_length = player.duration()
    # if the position is imposible, set it to 0
    if position <= 0 or position > full_length:
        position = 0.0
    player.set_position(position)
    # check and set duration
    length_to_end = player.duration()
    # if duration is imposible, set it to the length_to_end
    if duration == 0 or duration > length_to_end:
        wait = length_to_end - trim_from_end
    else:
        wait = duration
    if wait < 0:
        wait = 0
    debug("  full length: ", full_length)
    debug("  length to end: ", length_to_end)
    debug("  wait: ", wait)
    sleep(duration)
    debug("  post sleep pos:", player.position())
    #player.pause()
    #player.stop()
    debug("  post pause pos:", player.position())
    return True


def main():

    try:
        player = OMXPlayer(choice(trans_films))

        while True:
            play_film(player, choice(trans_films), duration=1)
            play_film(player, choice(rotate_films), duration=10)
        print "Done."

    except KeyboardInterrupt:
        # Kill the `omxplayer` process gracefully.
        player.quit()

if __name__ == "__main__":
    main()
