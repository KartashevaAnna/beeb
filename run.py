import os

import coloredlogs
import uvicorn
from loguru import logger

from app.settings import SETTINGS
from app.utils.welcome import WELCOME_MESSAGE

if __name__ == "__main__":
    coloredlogs.install(level=SETTINGS.server.log_level)
    logger.opt(colors=True).success(f"<cyan>{WELCOME_MESSAGE}</>")
    uvicorn.run(
        "app.application:build_app",
        port=os.getenv("server_port", SETTINGS.server.port),
        host=SETTINGS.server.host,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
