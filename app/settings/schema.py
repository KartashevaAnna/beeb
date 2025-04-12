from typing import Tuple, Type

from pydantic import BaseModel, ConfigDict, computed_field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)
from sqlalchemy import URL

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


class DatabaseSettings(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    dialect: str = "postgresql"
    host: str
    port: int
    database: str
    user: str
    password: str

    @computed_field
    @property
    def db_url(self) -> URL:
        return URL.create(
            self.dialect,
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
        )


class Urls(BaseModel):
    ping: str
    create_expense: str
    expense: str
    expenses: str
    update_expense: str
    delete_expense: str
    total_expenses: str
    total_expenses_monthly: str
    create_category: str
    category: str
    categories: str
    update_category: str


class Templates(BaseModel):
    read_expense: str
    read_expenses: str
    create_expense: str
    delete_expense: str
    total_expenses_monthly: str
    total_expenses: str
    create_category: str
    read_category: str
    read_categories: str


class Settings(CustomSettings):
    server: ServerSettings
    urls: Urls
    templates: Templates
    database: DatabaseSettings
