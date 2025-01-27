from typing import Tuple, Type

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from app.utils.tools.config_loader import load_custom_config_source


class CustomSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file_encoding="utf-8")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            load_custom_config_source,
            env_settings,
            file_secret_settings,
        )


class ServerSettings(BaseModel):
    host: str
    port: int
    debug: bool = False
    log_level: str = "critical"


class Urls(BaseModel):
    ping: str


class Settings(CustomSettings):
    server: ServerSettings
    urls: Urls
