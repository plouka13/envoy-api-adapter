# api_adapter
Adapter to perform invoice api requests + interface to envoy frontend

## Install
### Installing Python Poetry
Next, since this is a poetry based project, you will need to install poetry with the following then restart your terminal:

**mac**
```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

**windows**
```bash
(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python -
```

### Install Locally
To install all python dependencies needed, run:
```bash
poetry install
```
NOTE: ensure you have installed poetry first (see above in Prequisites)

Now setup pre-commit so that every time you make a commit, certain checks are run to ensure code quality & readability.
```bash
poetry run pre-commit install
```
## Running
Since python poetry is installed here, to run this project locally:
```bash
poetry run python api_adapter/main.py
```
## Testing
```bash
poetry run pytest
```

### Credits
This is the compiled works of team Eclair