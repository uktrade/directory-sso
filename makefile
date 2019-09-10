ARGUMENTS = $(filter-out $@,$(MAKECMDGOALS))

clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

pytest:
	ENV_FILES='dev,test' \
	pytest $(ARGUMENTS) \
	-n auto \
	--dist=loadfile \
	--ignore=node_modules \
	--cov=. \
	--cov-config=.coveragerc \
	--cov-report=term \
	--capture=no \
	--nomigrations \
	-Wignore::DeprecationWarning \
	-vv

flake8:
	flake8 . \
	--exclude=.venv,venv,node_modules,migrations \
	--max-line-length=120

manage:
	ENV_FILES='dev,secrets-do-not-commit' ./manage.py $(ARGUMENTS)

webserver:
	ENV_FILES='dev,secrets-do-not-commit' python manage.py runserver 0.0.0.0:8003 $(ARGUMENTS)

requirements:
	pip-compile requirements.in
	pip-compile requirements_test.in

install_requirements:
	pip install -r requirements_test.txt

css:
	./node_modules/.bin/gulp sass

init_secrets:
	cp conf/env/secrets-template conf/env/secrets-do-not-commit
	sed -i -e 's/#DO NOT ADD SECRETS TO THIS FILE//g' conf/env/secrets-do-not-commit

.PHONY: clean pytest flake8 manage webserver requirements install_requirements css
