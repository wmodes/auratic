import threading

class VideoThread(threading.Thread):
    """Thread class with a stop() method. The thread itself checks
    regularly for the stopped() condition."""

    def __init__(self, playlist=None,):
        super(VideoThread, self).__init__()
        self._stop = threading.Event()
        self._player_pgid_list = []
        if playlist:
            self.start_sequence(playlist)

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def start_sequence(self, playlist):
        if not isinstance(playlist, list):
            raise ValueError("Expecting a list")
        for video in playlist:
            if not self.stopped():
                self.__start_video__(video)

    def __start_video__(self, video):
        if not isinstance(playlist, dict):
            raise ValueError("Expecting a dictionary of video data")
        # start the video
        # store the video pgid so we can kill it if we have to
        # tight wait loop to check for stopped condition
        # kill all video(s) if necessary using the stored pgids


def main():
    films = [
        {'name': "idle_2",
            'file': "../media/idle_2.mp4",
            'type': 'loop',
            'start': 0.0,
            'length': 0.0,
            'layer': 1,
         },
        {'name': "tv-color-bars-distorted",
            'file': "../media/tv-color-bars-distorted.mp4",
            'type': 'transition',
            'start': 0.0,
            'length': 1.0,
            'layer': 9,
         },
        {'name': "tv-static-transition",
            'file': "../media/tv-static-transition.mp4",
            'type': 'transition',
            'start': 0.0,
            'length': 1.0,
            'layer': 9,
         },
        {'name': "1960s-baltimore-family",
            'file': "../media/1960s-baltimore-family.mp4",
            'type': 'content',
            'start': 0.0,
            'length': 5.0,
            'layer': 5,
         },
        ]
    print "Starting sequence"
    video = VideoThread()
    video.start_sequence([films[1], films[3], films[2]])
    print "Sequence started"

if __name__ == "__main__":
    main()