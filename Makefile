.PHONY: ruff
ruff:
	ruff format . && ruff check --fix .

.PHONY: local-run
local-run:
	CONFIG_SECRETS_PATH=./local.secrets.toml CONFIG_PATH=config.toml CONFIG_RENDERER=jinja2 python3 run.py
	
.PHONY: docker-run
docker-run:
	${MAKE} compose-down && ${MAKE} compose-up

.PHONY: compose-up
compose-up:
	docker-compose -f docker-compose.yml up --build

.PHONY: compose-down
compose-down:
	docker-compose -f docker-compose.yml rm -f