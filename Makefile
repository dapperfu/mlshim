VENV ?= .venv

${VENV}:
	python3 -mvenv ${@}
