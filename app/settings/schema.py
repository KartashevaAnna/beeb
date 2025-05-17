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
    debug: str
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
    signup: str
    login: str
    create_payment: str
    payment: str
    payments: str
    update_payment: str
    delete_payment: str
    total_payments_monthly: str
    create_category: str
    category: str
    categories: str
    update_category: str
    payments_dashboard: str
    payments_dashboard_yearly: str
    payments_dashboard_monthly: str
    home_page: str


class Templates(BaseModel):
    signup: str
    login: str
    read_payment: str
    read_payments: str
    create_payment: str
    delete_payment: str
    payments_dashboard_yearly: str
    payments_dashboard: str
    payments_dashboard_monthly: str
    create_category: str
    read_category: str
    read_categories: str
    home_page: str


class SecretsSettings(BaseModel):
    salt: str
    jwt_secret: str
    session_lifetime: int


class Settings(CustomSettings):
    server: ServerSettings
    urls: Urls
    templates: Templates
    database: DatabaseSettings
    secrets: SecretsSettings
