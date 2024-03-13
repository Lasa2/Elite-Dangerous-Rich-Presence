import os
from functools import wraps
from pathlib import Path

from loguru import logger
from pydantic import BaseModel, ConfigDict, validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    JsonConfigSettingsSource,
)

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
        settings.model_dump_json(), encoding=settings.model_config["env_file_encoding"]
    )


# def read_settings_json(settings: BaseSettings) -> dict[str, Any]:
#     encoding = settings.__config__.env_file_encoding
#     if SETTINGS_FILE.is_file():
#         return json.loads(Path("settings.json").read_text(encoding))
#     return dict()


class GeneralSettings(BaseModel):
    auto_tray: bool = False
    auto_close: bool = False
    check_updates: bool = True
    journal_path: Path = DEFAULT_JOURNAL_PATH
    log_level: str = "Info"

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

    model_config = ConfigDict(
        validate_assignment=True,
    )

    # class Config:
    #     validate_assignment = True


class RichPrensenceSettings(BaseModel):
    cmdr: bool = True
    power: bool = True
    location: bool = True
    gamemode: bool = True
    multicrew_mode: bool = True
    multicrew_size: bool = True
    time_elapsed: bool = True
    ship_icon: bool = True
    ship_text: bool = True


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

    model_config = ConfigDict(
        validate_assignment=True,
    )

    # class Config:
    #     validate_assignment = True


class Settings(BaseSettings):
    general: GeneralSettings = GeneralSettings()
    rich_presence: RichPrensenceSettings = RichPrensenceSettings()
    elite_dangerous: EliteDangerousSettings = EliteDangerousSettings()

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        json_file=SETTINGS_FILE,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: BaseSettings,
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            JsonConfigSettingsSource(settings_cls),
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

    # class Config:
    #     env_file_encoding = "utf-8"

    #     @classmethod
    #     def customise_sources(cls, init_settings, env_settings, file_secret_settings):
    #         return (
    #             init_settings,
    #             env_settings,
    #             file_secret_settings,
    #             read_settings_json,
    #         )


settings = Settings()


def save_afterwards(func):
    @wraps(func)
    async def save_settings(*args, **kwargs):
        await func(*args, **kwargs)
        logger.debug(settings.model_dump_json())
        write_settings_json(settings)

    return save_settings
