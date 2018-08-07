COMPOSE := $(shell command -v docker-compose 2> /dev/null)
POETRY := $(shell command -v poetry 2> /dev/null)

setup:
ifndef COMPOSE
	@echo "You must have poetry installed (https://github.com/sdispater/poetry)."
	@echo
	@exit 1
endif
	@poetry develop

deps:
ifdef COMPOSE
	@echo "Starting dependencies..."
	@docker-compose --project-name easyq up -d
	@echo "Dependencies started successfully."
endif

stop-deps:
ifdef COMPOSE
	@echo "Stopping dependencies..."
	@docker-compose --project-name easyq stop
	@docker-compose --project-name easyq rm -f
endif

test: deps
	@poetry run pytest --quiet --nf --cov=easyq tests/

watch:
	@poetry run ptw -c -w -- --quiet --nf --cov=easyq tests/

run:
	@easyq api