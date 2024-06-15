ifneq (,$(wildcard ./.env))
    include .env
    export
endif


install:
	poetry env use `which python3`
	poetry install

black:
	poetry run black hearts_textual tests

mypy:
	poetry run mypy

server:
	poetry run python -m hearts_textual.server

client:
	poetry run python -m hearts_textual.client

test:
	poetry run pytest --capture=no

.PHONY: install mypy test client server

