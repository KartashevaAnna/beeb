.PHONY: ruff
ruff:
	ruff format . && ruff check --fix . && isort .

.PHONY: local-run
local-run:
	CONFIG_SECRETS_PATH=./local.secrets.toml CONFIG_PATH=config.toml CONFIG_RENDERER=jinja2 python3 run.py
	
.PHONY: product-run
product-run:
	CONFIG_SECRETS_PATH=./product.secrets.toml CONFIG_PATH=config.toml CONFIG_RENDERER=jinja2 python3 run.py
	
.PHONY: compose-up
compose-up:
	docker-compose -f docker-compose.yml up --build


.PHONY: compose-down
compose-down:
	docker-compose -f docker-compose.yml rm -f

.PHONY: run-tests
run-tests:
	docker-compose -f tests/docker-compose.local.yml up --abort-on-container-exit --remove-orphans

.PHONY: build-tests
build-tests:
	docker-compose -f tests/docker-compose.local.yml build

.PHONY: teardown-tests
teardown-tests:
	docker-compose -f tests/docker-compose.local.yml rm -f


.PHONY: docker-run
docker-run:
	${MAKE} compose-down && ${MAKE} compose-up


.PHONY: tests
tests:
	${MAKE} teardown-tests && ${MAKE} build-tests && ${MAKE} run-tests && ${MAKE} teardown-tests


.PHONY: compose-one-up
compose-one-up:
	docker-compose -f docker-compose.local.small.yml up --build


.PHONY: compose-one-down
compose-one-down:
	docker-compose -f docker-compose.local.small.yml rm -f

.PHONY: run-test
run-test:
	docker-compose -f tests/docker-compose.local.small.yml up --abort-on-container-exit --remove-orphans

.PHONY: build-test
build-test:
	docker-compose -f tests/docker-compose.local.small.yml build

.PHONY: teardown-test
teardown-test:
	docker-compose -f tests/docker-compose.local.small.yml rm -f


.PHONY: docker-test-run
docker-test-run:
	${MAKE} compose-one-down && ${MAKE} compose-one-up


.PHONY: test
test:
	${MAKE} teardown-test && ${MAKE} build-test && ${MAKE} run-test && ${MAKE} teardown-test