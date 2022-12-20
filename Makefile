ifneq (,$(wildcard ./.env))
    include .env
    export
endif


install:
	poetry env use `which python3.11`
	poetry install

mypy:
	poetry run mypy

server:
	poetry run python -m hearts-textual.server

client:
	poetry run python -m hearts-textual.client

test:
	poetry run pytest --capture=no

.PHONY: install mypy test client server

