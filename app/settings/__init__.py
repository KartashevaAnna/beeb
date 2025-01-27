from functools import lru_cache
from pathlib import Path

from jinja2_fragments.fastapi import Jinja2Blocks

from app.settings.schema import Settings


@lru_cache
def get_settings():
    return Settings()


SETTINGS = get_settings()


TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
TEMPLATES = Jinja2Blocks(directory=TEMPLATES_DIR)
TEMPLATES.env.globals["URLS"] = SETTINGS.urls
