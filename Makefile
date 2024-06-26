ifneq (,$(wildcard ./.env))
    include .env
    export
endif


tui:
	poetry run python tui/app.py

install:
	poetry env use `which python3`
	poetry install

black:
	poetry run black tui hearts_textual tests

mypy:
	poetry run mypy

server:
	poetry run python -m hearts_textual.server

client:
	poetry run python -m hearts_textual.client

test:
	poetry run pytest --capture=no

.PHONY: install mypy test client server tui black

