import os

import uvicorn

from app.settings import SETTINGS

if __name__ == "__main__":
    uvicorn.run(
        "app.application:build_app", port=os.getenv("server_port", SETTINGS.server.port), host=SETTINGS.server.host
    )
