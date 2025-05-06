from functools import lru_cache
from pathlib import Path

from jinja2_fragments.fastapi import Jinja2Blocks
from sqlalchemy import create_engine

from app.settings.schema import Settings


@lru_cache
def get_settings():
    return Settings()


SETTINGS = get_settings()

ENGINE = create_engine(
    url=SETTINGS.database.db_url, echo=eval(SETTINGS.server.debug)
)

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
PAYMENTS_TO_UPLOAD_DIR = Path(__file__).parent.parent / "payments_to_upload"
TEMPLATES = Jinja2Blocks(directory=TEMPLATES_DIR)
TEMPLATES.env.globals["URLS"] = SETTINGS.urls
