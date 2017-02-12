import kivy
kivy.require('1.9.0')

from kivy.app import App
from kivy.uix.video import Video
from kivy.config import Config

# small.3gp   small.flv   small.mp4   small.ogv   small.webm
filename = 'small.mp4'
options = {'eos': 'loop'}


Config.set('graphics', 'borderless', 1)
Config.set('graphics', 'fullscreen', 'auto')
Config.set('graphics', 'rotation', 90)
Config.write()


class MyApp(App):
    # def build_config(self, config):
    #     config.setdefaults('graphics', {
    #         'borderless': 1,
    #         'fullscreen': 'auto',
    #         'rotation': 90
    #     })
    def build(self):
        # config = self.config
        video = Video(source=filename)
        video.state = 'play'
        video.options = {'eos': 'loop'}
        video.allow_stretch = True
        return video


if __name__ == '__main__':
    MyApp().run()