from os.path import isfile
import yaml
from trayicon import TrayIcon
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty, DictProperty
from kivy.app import App
import win32gui
import asyncio
from kivy.config import Config
from multiprocessing import Process, Lock
from threading import Thread


Config.set("graphics", "resizable", False)
Config.set("graphics", "height", 600)
Config.set("graphics", "width", 800)
#Config.set("kivy", "log_level", "debug")


class ToggleOption(BoxLayout):
    state = BooleanProperty(True)

    def toggle_state(self):
        self.state = not self.state

    def get_setting(self):
        return self.state


class TextOption(BoxLayout):

    def get_setting(self):
        return self.input.text


class EliteDangerousRichPresence(Widget):
    settings = DictProperty()

    def __init__(self, **kwargs):
        self.load_settings()
        super().__init__(**kwargs)

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


class EliteDangerousRichPresenceApp(App):
    def build(self):
        return EliteDangerousRichPresence()

    @staticmethod
    def rgba(r, g, b, a):
        return r / 255.0, g / 255.0, b / 255.0, a / 255.0

    @staticmethod
    def hex(hex):
        rgb = tuple((int(hex[1:][i:i + 2], 16) for i in (0, 2, 4)))
        return EliteDangerousRichPresenceApp.rgba(*rgb, 255)


class BackgroundApp():
    open_settings: bool = False

    def set_open_settings(self, bool):
        self.open_settings = bool

    async def app_func(self):
        self.tray = TrayIcon(
            name="Elite Dangerous Rich Presence", settings=self.set_open_settings)

        code = 0
        while code == 0:
            code = win32gui.PumpWaitingMessages()
            if self.open_settings:
                self.open_settings = False
                #Process(target=EliteDangerousRichPresenceApp().run()).start()
                proc = Thread(target=EliteDangerousRichPresenceApp().run())
                proc.start()
                print("done")


if __name__ == '__main__':
    asyncio.run(BackgroundApp().app_func())
    # w = TrayIcon(name="Elite Dangerous Rich Presence")
    # win32gui.PumpMessages()
    # edrpc_app = EliteDangerousRichPresenceApp()
    # edrpc_app.run()
