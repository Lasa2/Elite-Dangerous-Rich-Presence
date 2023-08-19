import json
import os
from functools import wraps
from pathlib import Path
from typing import Any

from loguru import logger
from pydantic import BaseModel, ConfigDict, FieldValidationInfo, field_validator
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

from elite_dangerous_rich_presence.util import LaunchMode

SETTINGS_FILE = Path("settings.json")
DEFAULT_JOURNAL_PATH = Path(
    os.environ["USERPROFILE"],
    "Saved Games",
    "Frontier Developments",
    "Elite Dangerous",
)


class JsonConfigSettingsSource(PydanticBaseSettingsSource):
    """
    A simple settings source class that loads variables from a JSON file
    at the project's root.
    """

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> tuple[Any, str, bool]:
        encoding = self.config.get("env_file_encoding")
        file_content_json = json.loads(SETTINGS_FILE.read_text(encoding))
        field_value = file_content_json.get(field_name)
        return field_value, field_name, False

    def prepare_field_value(
        self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
    ) -> Any:
        return value

    def __call__(self) -> dict[str, Any]:
        d: dict[str, Any] = {}

        if not SETTINGS_FILE.is_file():
            return d

        for field_name, field in self.settings_cls.model_fields.items():
            field_value, field_key, value_is_complex = self.get_field_value(
                field, field_name
            )
            field_value = self.prepare_field_value(
                field_name, field, field_value, value_is_complex
            )
            if field_value is not None:
                d[field_key] = field_value

        return d


def write_settings_json(settings: BaseSettings) -> None:
    SETTINGS_FILE.write_text(
        settings.model_dump_json(), encoding=settings.model_config["env_file_encoding"]
    )


def read_settings_json(settings: BaseSettings) -> dict[str, Any]:
    encoding = settings.model_config["env_file_encoding"]
    if SETTINGS_FILE.is_file():
        return json.loads(Path("settings.json").read_text(encoding))
    return dict()


class GeneralSettings(BaseModel):
    auto_tray: bool = False
    auto_close: bool = False
    check_updates: bool = True
    journal_path: Path = DEFAULT_JOURNAL_PATH
    log_level: str = "Info"

    model_config = ConfigDict(validate_assignment=True)

    @field_validator("journal_path")
    @classmethod
    def path_exists(cls, v: str | Path) -> Path:
        if v == DEFAULT_JOURNAL_PATH:
            Path(v).mkdir(parents=True, exist_ok=True)
        path = Path(os.path.expandvars(v))
        if not path.exists():
            raise ValueError("Journal Path: Path does not exists")
        if not path.is_dir():
            raise ValueError("Journal Path: Path is not a directory")
        return path


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

    model_config = ConfigDict(validate_assignment=True)

    @field_validator("launch_mode", mode="before")
    @classmethod
    def launch_mode_validator(cls, v: int | LaunchMode) -> int:
        if isinstance(v, LaunchMode):
            return v.value
        return v

    @field_validator("path")
    @classmethod
    def path_valid(cls, v: str | Path, info: FieldValidationInfo) -> str | Path:
        if v == "" or info.data.get("launch_mode") is not LaunchMode.EXECUTABLE:
            return v
        path = Path(os.path.expandvars(v))
        if not path.exists():
            raise ValueError("Elite Dangerous Path: Path does not exists")
        if not path.is_file():
            raise ValueError("Elite Dangerous Path: Path is not a valid file")
        return path


class Settings(BaseSettings):
    general: GeneralSettings = GeneralSettings()
    rich_presence: RichPrensenceSettings = RichPrensenceSettings()
    elite_dangerous: EliteDangerousSettings = EliteDangerousSettings()

    model_config = ConfigDict(env_file_encoding="utf-8")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            JsonConfigSettingsSource(settings_cls),
        )


settings = Settings()


def save_afterwards(func):
    @wraps(func)
    async def save_settings(*args, **kwargs):
        await func(*args, **kwargs)
        logger.debug(settings.json())
        write_settings_json(settings)

    return save_settings
