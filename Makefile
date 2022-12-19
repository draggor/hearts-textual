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
	poetry run python src/server.py

client:
	poetry run python src/client.py

test:
	poetry run pytest --capture=no

.PHONY: install mypy test client server

