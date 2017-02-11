from omxplayer import OMXPlayer
from time import sleep
from random import choice 
file_path_or_url = 'small.mp4'

from video_db import *

DEBUG = True

transition_film_list = []
content_film_list = []


def debug(*args):
    if (DEBUG):
        text = " ".join(list(map(str, args)))
        print text


def create_film_lists():
    for film in films.values():
        if film['type'] == 'transition':
            transition_film_list.append(film)
        elif film['type'] == 'content':
            content_film_list.append(film)


def play_film_object(player, film):
    debug("\nfilename:", film['name'])
    debug("  type", film['type'])
    debug("  start:", film['start'])
    debug("  end:", film['start']+film['length'])
    debug("  length:", film['length'])
    player.set_position(film['start'])
    debug("  pre-play pos:", player.position())
    if not player.is_playing():
        player.play()
    sleep(film['length'])
    # while (player.position() < film['start']+film['length']):
    #     pass
    debug("  post wait pos:", player.position())
    #player.pause()
    return True


def main():

    create_film_lists()
    print transition_film_list
    print content_film_list

    try:
        player = OMXPlayer(one_big_film)

        while True:
            play_film_object(player, choice(transition_film_list))
            play_film_object(player, choice(content_film_list))
        print "Done."

    except KeyboardInterrupt:
        # Kill the `omxplayer` process gracefully.
        player.quit()

if __name__ == "__main__":
    main()
