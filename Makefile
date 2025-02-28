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

.PHONY: tests
tests:
	${MAKE} teardown-tests && ${MAKE} build-tests && ${MAKE} run-tests && ${MAKE} teardown-tests

.PHONY: run-tests
run-tests:
	docker-compose -f tests/functional/docker-compose.local.yml up --abort-on-container-exit --remove-orphans

.PHONY: build-tests
build-tests:
	docker-compose -f tests/functional/docker-compose.local.yml build

.PHONY: teardown-tests
teardown-tests:
	docker-compose -f tests/functional/docker-compose.local.yml rm -f


.PHONY: small-test
small-test:
		docker-compose -f tests/functional/docker-compose.local.small.yml up --abort-on-container-exit --remove-orphans

.PHONY: small-tests
small-tests:
	${MAKE} teardown-tests && ${MAKE} build-tests && ${MAKE} small-test && ${MAKE} teardown-tests