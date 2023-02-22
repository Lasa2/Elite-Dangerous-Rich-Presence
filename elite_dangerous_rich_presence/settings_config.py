import json
import os
from functools import wraps
from pathlib import Path
from typing import Any

from loguru import logger
from pydantic import BaseModel, BaseSettings, validator

from elite_dangerous_rich_presence.util import LaunchMode

SETTINGS_FILE = Path("settings.json")
DEFAULT_JOURNAL_PATH = Path(
    os.environ["USERPROFILE"],
    "Saved Games",
    "Frontier Developments",
    "Elite Dangerous",
)


def write_settings_json(settings: BaseSettings) -> None:
    SETTINGS_FILE.write_text(
        settings.json(), encoding=settings.__config__.env_file_encoding
    )


def read_settings_json(settings: BaseSettings) -> dict[str, Any]:
    encoding = settings.__config__.env_file_encoding
    if SETTINGS_FILE.is_file():
        return json.loads(Path("settings.json").read_text(encoding))
    return dict()


class GeneralSettings(BaseModel):
    auto_tray = False
    auto_close = False
    journal_path = DEFAULT_JOURNAL_PATH
    log_level = "Info"

    @validator("journal_path")
    def path_exists(cls, v: str | Path) -> Path:
        if v == DEFAULT_JOURNAL_PATH:
            Path(v).mkdir(parents=True, exist_ok=True)
        path = Path(os.path.expandvars(v))
        if not path.exists():
            raise ValueError("Journal Path: Path does not exists")
        if not path.is_dir():
            raise ValueError("Journal Path: Path is not a directory")
        return path

    class Config:
        validate_assignment = True


class RichPrensenceSettings(BaseModel):
    cmdr = True
    power = True
    location = True
    gamemode = True
    multicrew_mode = True
    multicrew_size = True
    time_elapsed = True
    ship_icon = True
    ship_text = True


class EliteDangerousSettings(BaseModel):
    arguments: str = ""
    auto_launch: bool = False
    launch_mode: LaunchMode = LaunchMode.EXECUTABLE
    path: str | Path = ""

    @validator("path")
    def path_valid(cls, v: str | Path, values) -> str | Path:
        if v == "" or values.get("launch_mode") is not LaunchMode.EXECUTABLE:
            return v
        path = Path(os.path.expandvars(v))
        if not path.exists():
            raise ValueError("Elite Dangerous Path: Path does not exists")
        if not path.is_file():
            raise ValueError("Elite Dangerous Path: Path is not a valid file")
        return path

    @validator("launch_mode", pre=True)
    def launch_mode_validator(cls, v: int | LaunchMode) -> int:
        if isinstance(v, LaunchMode):
            return v.value
        return v

    class Config:
        validate_assignment = True


class Settings(BaseSettings):
    general = GeneralSettings()
    rich_presence = RichPrensenceSettings()
    elite_dangerous = EliteDangerousSettings()

    class Config:
        env_file_encoding = "utf-8"

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return (
                init_settings,
                env_settings,
                file_secret_settings,
                read_settings_json,
            )


settings = Settings()


def save_afterwards(func):
    @wraps(func)
    async def save_settings(*args, **kwargs):
        await func(*args, **kwargs)
        logger.debug(settings.json())
        write_settings_json(settings)

    return save_settings
