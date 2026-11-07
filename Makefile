.PHONY: run_app_local

NETWORK_NAME ?= movies_net
MESSAGE ?= "some_migration"
DOWN_NUM ?= -1

ALEMBIC_CMD := alembic
SHELL := /bin/bash

run_app_local:
	@python main.py

migrate_create:
	@$(ALEMBIC_CMD) revision --autogenerate -m "$(MESSAGE)"

migrate_upgrade:
	@$(ALEMBIC_CMD) upgrade head

migrate_downgrade:
	@$(ALEMBIC_CMD) downgrade $(DOWN_NUM)

test_realm_token:
	@echo bc248ba1cec616298d82b0336960b704dfd9f77e423266d284c0df801f01b278