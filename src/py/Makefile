STYLE_CHECK_PYTHON_CODE_DIRECTORIES = . workflows
STYLE_CHECK_PYTHON_CODE_SKIPPED_DIRECTORIES = third-party
TYPE_CHECK_BASE_PYTHON_CODE_DIRECTORIES = aspen
TYPE_CHECK_INDIVIDUAL_PYTHON_CODE_DIRECTORIES = database_migrations $(shell ls -d workflows/*)


### CHECK STYLE #############################################
check-style: lint black isort mypy

lint:
	flake8 --ignore "E203, E231, E501, W503" $(STYLE_CHECK_PYTHON_CODE_DIRECTORIES) --exclude third-party

black:
	black --check $(STYLE_CHECK_PYTHON_CODE_DIRECTORIES) --exclude $(STYLE_CHECK_PYTHON_CODE_SKIPPED_DIRECTORIES)

isort:
	isort --profile black --check $(STYLE_CHECK_PYTHON_CODE_DIRECTORIES) --skip $(STYLE_CHECK_PYTHON_CODE_SKIPPED_DIRECTORIES) 

MYPY_TARGETS = $(foreach stylecheckdir, $(TYPE_CHECK_INDIVIDUAL_PYTHON_CODE_DIRECTORIES), mypy-$(stylecheckdir))

mypy: mypy-base $(MYPY_TARGETS)

mypy-base:
	mypy --ignore-missing-imports $(TYPE_CHECK_BASE_PYTHON_CODE_DIRECTORIES)

$(MYPY_TARGETS): mypy-%: mypy-base
	mypy --ignore-missing-imports $(TYPE_CHECK_BASE_PYTHON_CODE_DIRECTORIES) $*


### RUN STYLE #############################################
run-style: run-black run-isort

run-black:
	black $(STYLE_CHECK_PYTHON_CODE_DIRECTORIES) --exclude $(STYLE_CHECK_PYTHON_CODE_SKIPPED_DIRECTORIES)

run-isort:
	isort --profile black $(STYLE_CHECK_PYTHON_CODE_DIRECTORIES) --skip $(STYLE_CHECK_PYTHON_CODE_SKIPPED_DIRECTORIES) 


### TESTING #############################################
test: # run pytest
	pytest -n8 aspen

### ALEMBIC #############################################
alembic-upgrade-head:
	alembic upgrade head # applies to local only


alembic-autogenerate:
	alembic revision --autogenerate -m "$(MESSAGE)" --rev-id $$(date +%Y%m%d_%H%M%S)

.PHONY: init-db-cli
init-db-cli:
	apt-get install -y git
	# TODO - temporary hack until sqlalchemy-utils gets updated for sqlalchemy 1.4+
	# We're waiting on this PR: https://github.com/kvesteri/sqlalchemy-utils/pull/506
	pip uninstall -y sqlalchemy-utils
	pip install git+https://github.com/kvesteri/sqlalchemy-utils@c76256c64957aa3881fb9fcc58e2d8a41b914505
	pip install .

.PHONY: db-migrations
db-migrations: init-db-cli
	if [ ! -z "${DATA_LOAD_PATH}" ]; then \
		apt-get install -y postgresql-client; \
		aspen-cli db --remote setup; \
	fi
	DB=remote alembic upgrade head

.PHONY: db-drop
db-drop: init-db-cli
	aspen-cli db --remote drop
