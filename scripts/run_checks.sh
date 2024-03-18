echo Run Black.
poetry run black api_adapter tests --check

echo Run Flake8.
poetry run flake8 api_adapter tests

echo Run Unit tests.
poetry run pytest tests
