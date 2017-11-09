
VENV ?= .venv
PYTHON ?= python3

${VENV}:
	${PYTHON} -mvenv ${VENV}