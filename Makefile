.PHONY: setup clean test coverage run lint install setup-dev

# Variables
PYTHON = python3
VENV = venv
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest
RUFF = $(VENV)/bin/ruff

setup:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install -r requirements.txt

setup-dev: setup
	$(PIP) install -r test_requirements.txt
	$(PIP) install ruff

test:
	$(PYTEST) --cov=src test/ -v

run:
	$(PYTHON) -m src.senate_scraper

clean:
	rm -rf $(VENV)
	rm -rf __pycache__
	rm -rf src/__pycache__
	rm -rf test/__pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf senate_reports_*.json

check:
	$(RUFF) check src/ test/

format:
	$(RUFF) format src/ test/

lint: check format
