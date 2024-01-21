ARGUMENTS = $(filter-out $@,$(MAKECMDGOALS)) $(filter-out --,$(MAKEFLAGS))

clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

# configuration for black and isort is in pyproject.toml
autoformat:
	isort $(PWD)
	black $(PWD)

checks:
	isort $(PWD) --check
	black $(PWD) --check --verbose
	flake8 .

pytest:
	ENV_FILES='test,dev' pytest $(ARGUMENTS)

# Usage: make pytest_single <path_to_file>::<method_name>
pytest_single:
	ENV_FILES='test,dev' \
	pytest \
	    $(ARGUMENTS)
		--junit-xml=./results/pytest_unit_report.xml \
		--cov-config=.coveragerc \
		--cov-report=html \
		--cov=. \

pytest_codecov:
	ENV_FILES='test,dev' \
	pytest \
		--cov-config=.coveragerc \
		--cov-report=term \
		--cov=. \
		--codecov \
		$(ARGUMENTS)

flake8:
	flake8 . \
	--exclude=.venv,venv,node_modules,migrations \
	--max-line-length=120

manage:
	ENV_FILES='secrets-do-not-commit,dev' ./manage.py $(ARGUMENTS)

webserver:
	ENV_FILES='secrets-do-not-commit,dev' python manage.py runserver 0.0.0.0:8003 $(ARGUMENTS)

requirements:
	pip-compile requirements.in
	pip-compile requirements_test.in

install_requirements:
	pip install -r requirements_test.txt

css:
	./node_modules/.bin/gulp sass

secrets:
	@if [ ! -f ./conf/env/secrets-do-not-commit ]; \
		then sed -e 's/#DO NOT ADD SECRETS TO THIS FILE//g' conf/env/secrets-template > conf/env/secrets-do-not-commit \
			&& echo "Created conf/env/secrets-do-not-commit"; \
		else echo "conf/env/secrets-do-not-commit already exists. Delete first to recreate it."; \
	fi

worker:
	ENV_FILES='secrets-do-not-commit,dev' celery -A conf worker -B -l debug

beat:
	ENV_FILES='secrets-do-not-commit,dev' celery -A conf beat -l info -S django


.PHONY: clean autoformat checks pytest manage webserver requirements install_requirements css secrets worker beat


pytest-docker:
	ENV_FILES='secrets-do-not-commit,test,dev' pytest $(ARGUMENTS)