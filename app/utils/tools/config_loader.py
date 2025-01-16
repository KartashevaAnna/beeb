import os
import pathlib
from pathlib import Path
from typing import Any

import tomllib
from jinja2 import Template


def get_config_path(config_path: Path) -> Path:
    return pathlib.Path(os.getenv("CONFIG_PATH", config_path)).absolute()


def render_secrets(context, secrets) -> dict:
    rendered = Template(context).render(
        parameters=secrets["parameters"],
        secrets=secrets["secrets"],
    )
    return tomllib.loads(rendered)


def read_secrets() -> dict:
    secrets_path = pathlib.Path(os.environ["CONFIG_SECRETS_PATH"]).absolute()
    return dict(tomllib.loads(secrets_path.read_text()))


def read_context(config_path) -> str:
    with get_config_path(config_path).open() as f:
        context = f.read()
    return context


def load_config(config_path):
    context = read_context(config_path)
    secrets = read_secrets()
    return render_secrets(context, secrets)


def load_custom_config_source(*args, **kwargs) -> dict[str, Any]:
    return load_config(config_path=Path(__file__).parent.parent / "config.toml")
