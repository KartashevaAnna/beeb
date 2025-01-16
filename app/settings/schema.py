from typing import Tuple

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
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
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


class Settings(CustomSettings):
    server: ServerSettings
