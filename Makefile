.PHONY: ruff
ruff:
	ruff format . && ruff check --fix .

.PHONY: local-run
local-run:
	CONFIG_SECRETS_PATH=./local.secrets.toml CONFIG_PATH=config.toml CONFIG_RENDERER=jinja2 python3 run.py
	# poetry run uvicorn app.application:app --reload