build: docker_test

heroku_deploy:
	heroku container:push web

clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

test_requirements:
	pip install -r requirements_test.txt

FLAKE8 := flake8 . --exclude=migrations
PYTEST := pytest . --cov=. $(pytest_args)
COLLECT_STATIC := python manage.py collectstatic --noinput

test:
	$(COLLECT_STATIC) && $(FLAKE8) && $(PYTEST)

DJANGO_WEBSERVER := \
	python manage.py migrate; \
	python manage.py runserver 0.0.0.0:$$PORT

django_webserver:
	$(DJANGO_WEBSERVER)

DOCKER_COMPOSE_REMOVE_AND_PULL := docker-compose -f docker-compose.yml -f docker-compose-test.yml rm -f && docker-compose -f docker-compose.yml -f docker-compose-test.yml pull
DOCKER_COMPOSE_CREATE_ENVS := ./docker/create_envs.sh

docker_run:
	$(DOCKER_COMPOSE_CREATE_ENVS) && \
	$(DOCKER_COMPOSE_REMOVE_AND_PULL) && \
	docker-compose up --build

DOCKER_SET_DEBUG_ENV_VARS := \
	export SSO_PORT=8003; \
	export SSO_DEBUG=true; \
	export SSO_SECRET_KEY=debug; \
	export SSO_POSTGRES_USER=debug; \
	export SSO_POSTGRES_PASSWORD=debug; \
	export SSO_POSTGRES_DB=sso_debug; \
	export SSO_DATABASE_URL=postgres://debug:debug@postgres:5432/sso_debug

DOCKER_REMOVE_ALL := \
	docker ps -a | \
	grep -e sso_ | \
	awk '{print $$1 }' | \
	xargs -I {} docker rm -f {}

docker_remove_all:
	$(DOCKER_REMOVE_ALL)

docker_debug: docker_remove_all
	$(DOCKER_SET_DEBUG_ENV_VARS) && \
	$(DOCKER_COMPOSE_CREATE_ENVS) && \
	docker-compose pull && \
	docker-compose build && \
	docker-compose run --service-ports webserver make django_webserver

docker_webserver_bash:
	docker exec -it sso_webserver_1 sh

docker_psql:
	docker-compose run postgres psql -h postgres -U debug

docker_test: docker_remove_all
	$(DOCKER_SET_DEBUG_ENV_VARS) && \
	$(DOCKER_COMPOSE_CREATE_ENVS) && \
	$(DOCKER_COMPOSE_REMOVE_AND_PULL) && \
	docker-compose -f docker-compose-test.yml build && \
	docker-compose -f docker-compose-test.yml run sut

DEBUG_SET_ENV_VARS := \
	export SECRET_KEY=debug; \
	export PORT=8003; \
	export DEBUG=true; \
	export DB_NAME=sso_debug; \
	export DB_USER=debug; \
	export DB_PASSWORD=debug; \
	export DATABASE_URL=postgres://debug:debug@localhost:5432/sso_debug

debug_webserver:
	 $(DEBUG_SET_ENV_VARS); $(DJANGO_WEBSERVER);

DEBUG_CREATE_DB := \
	psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$$DB_NAME'" | \
	grep -q 1 || psql -U postgres -c "CREATE DATABASE $$DB_NAME"; \
	psql -U postgres -tc "SELECT 1 FROM pg_roles WHERE rolname = '$$DB_USER'" | \
	grep -q 1 || echo "CREATE USER $$DB_USER WITH PASSWORD '$$DB_PASSWORD'; GRANT ALL PRIVILEGES ON DATABASE \"$$DB_NAME\" to $$DB_USER; ALTER USER $$DB_USER CREATEDB" | psql -U postgres

debug_db:
	$(DEBUG_SET_ENV_VARS) && $(DEBUG_CREATE_DB)

debug_test:
	$(DEBUG_SET_ENV_VARS) && $(FLAKE8) && $(PYTEST)

debug: test_requirements debug_db debug_test

.PHONY: build clean test_requirements docker_test docker_run docker_debug docker_webserver_bash docker_psql docker_test debug_webserver debug_db debug_test debug
