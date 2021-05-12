import logging
import os
import re
import yaml

from BackgroundApp import logging_conf  # noqa # nopep8
os.environ["KCFG_KIVY_LOG_LEVEL"] = logging_conf["root"]["level"].lower()
# noqa # nopep8

from kivy.app import App  # noqa
from kivy.clock import Clock  # noqa
from kivy.config import Config  # noqa
from kivy.properties import BooleanProperty, DictProperty, StringProperty  # noqa
from kivy.uix.boxlayout import BoxLayout  # noqa
from kivy.uix.widget import Widget  # noqa

logger = logging.getLogger(__name__)

Config.set("graphics", "resizable", False)
Config.set("graphics", "height", 600)
Config.set("graphics", "width", 800)


class ToggleOption(BoxLayout):
    state = BooleanProperty(True)

    def toggle_state(self):
        self.state = not self.state

    def get_setting(self):
        return self.state


class LoggingOption(BoxLayout):
    state = StringProperty("WARNING")

    def set_state(self, state):
        self.state = state

    def get_setting(self):
        return self.state


class TextOption(BoxLayout):
    def get_setting(self):
        return self.input.text

    def on_focus(self):
        return

    def validate_path(self):
        if not self.input.focus:
            var = re.search("%(.+?)%", self.input.text)
            if var is not None:
                self.input.text = self.input.text.replace(
                    f"%{var.group(1)}%", os.environ[var.group(1)])

            if not os.path.exists(self.input.text) and self.input.text != "":
                logger.warning("Invalid path: %s", self.input.text)

    def validate_executable(self):
        self.validate_path()
        if not self.input.focus:
            arg_inst = self.parent.parent.ids["elite_dangerous.arguments"]
            if self.input.text.endswith(".exe") or self.input.text == "":
                arg_inst.disabled = False
            else:
                arg_inst.disabled = True


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
                logger.debug("Main application closed, closing window")
                App.get_running_app().stop()

    def load_settings(self):
        with open("settings.yaml", "r") as stream:
            try:
                data = yaml.safe_load(stream)
                self.settings = data
            except yaml.YAMLError as e:
                logger.error("Unable to read settings.yaml, %s", e)

    def save_settings(self):
        # self.convert_paths()
        settings = dict()
        for entry in self.ids:
            if "." in entry:
                cat, sett = entry.split(".")
                if cat not in settings:
                    settings[cat] = dict()
                settings[cat][sett] = self.ids[entry].get_setting()
        with open("settings.yaml", "w") as stream:
            try:
                stream.write(yaml.dump(settings))
            except yaml.YAMLError as e:
                logger.error("Unable to save settings.yaml, %s", e)
        self.con.send("changed_settings")

        def reset(dt):
            self.ids["savebutton"].text = "Save Options"
        self.ids["savebutton"].text = "Saved!"
        Clock.schedule_once(reset, 2)


class SettingsApp(App):
    def __init__(self, con):
        self.con = con
        super().__init__()

    def build(self):
        self.title = "Elite Dangerous Rich Presence Settings"
        self.icon = "elite-dangerous-clean.ico"
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
