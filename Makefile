ifneq (,$(wildcard ./.env))
    include .env
    export
endif

PYTHON_VERSION ?= python3

tui:
	poetry run python tui/app.py

install:
	poetry env use `which ${PYTHON_VERSION}`
	poetry install

black:
	poetry run black tui hearts_textual tests

mypy:
	poetry run mypy

server:
	poetry run python -m hearts_textual.server

bots:
	poetry run python -m hearts_textual.server --bots

client:
	poetry run python -m hearts_textual.client

test:
	poetry run pytest --capture=no

.PHONY: install mypy test client server tui black bots

