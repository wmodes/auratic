from omxplayer import OMXPlayer
from time import sleep
from random import choice 
file_path_or_url = 'small.mp4'

from video_db import *

DEBUG = True

trans_films = []

content_films = []



def debug(*args):
    if (DEBUG):
        text = " ".join(list(map(str, args)))
        print text


def create_film_lists():
    for film in films:
        if film['type'] == 'transition':
            trans_films.append(film)
        elif film['content'] == 'transition':
            content_films.append(film)


def play_film_object(player, film):
    debug("\nfilename:", film['name'])
    debug("  type", film['type'])
    debug("  start:", film['start'])
    debug("  end:", film['start']+film['length'])
    debug("  length:", film['length'])
    player.set_position(film['start'])
    debug("  pre-play pos:", player.position())
    player.play()
    while (player.position() < film['start']+film['length']):
        pass
    debug("  post wait pos:", player.position())
    #player.pause()
    return True


def main():

    try:
        player = OMXPlayer(one_big_film)

        while True:
            play_film(player, choice(trans_films))
            play_film(player, choice(rotate_films))
        print "Done."

    # except KeyboardInterrupt:
    #     # Kill the `omxplayer` process gracefully.
    #     player.quit()

if __name__ == "__main__":
    main()
