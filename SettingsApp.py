from os.path import isfile
from kivy.clock import Clock
import yaml

from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty, DictProperty
from kivy.app import App

from kivy.config import Config


Config.set("graphics", "resizable", False)
Config.set("graphics", "height", 600)
Config.set("graphics", "width", 800)


class ToggleOption(BoxLayout):
    state = BooleanProperty(True)

    def toggle_state(self):
        self.state = not self.state

    def get_setting(self):
        return self.state


class TextOption(BoxLayout):

    def get_setting(self):
        return self.input.text


class Settings(Widget):
    settings = DictProperty()

    def __init__(self, con):
        from kivy.core.window import Window
        self.Window = Window
        self.con = con
        Clock.schedule_interval(self.check_queue, 0.5)
        self.load_settings()
        super().__init__()

    def check_queue(self, dt):
        if self.con.poll():
            msg = self.con.recv()
            if msg == "restore":
                self.Window.minimize()
                self.Window.restore()
            elif msg == "closed":
                App.get_running_app().stop()

    def load_settings(self):
        if not isfile("settings.yaml"):
            with open("settings.yaml", "w") as stream:
                stream.write("")
        with open("settings.yaml", "r") as stream:
            try:
                data = yaml.safe_load(stream)
                self.settings = data if data is not None else dict()
            except yaml.YAMLError as e:
                print(e)

    def save_settings(self):
        settings = dict()
        for entry in self.ids:
            cat, sett = entry.split(".")
            if cat not in settings:
                settings[cat] = dict()
            settings[cat][sett] = self.ids[entry].get_setting()
        with open("settings.yaml", "w") as stream:
            try:
                stream.write(yaml.dump(settings))
            except yaml.YAMLError as e:
                print(e)
        self.con.send("changed_settings")


class SettingsApp(App):
    def __init__(self, con):
        self.con = con
        super().__init__()

    def build(self):
        self.title = "Elite Dangerous Rich Presence Settings"
        return Settings(self.con)

    @staticmethod
    def rgba(r, g, b, a):
        return r / 255.0, g / 255.0, b / 255.0, a / 255.0

    @staticmethod
    def hex(hex):
        rgb = tuple((int(hex[1:][i:i + 2], 16) for i in (0, 2, 4)))
        return SettingsApp.rgba(*rgb, 255)

    def on_start(self):
        pass

    def on_stop(self):
        pass
