build: docker_test

clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

test_requirements:
	pip install -r requirements_test.txt

FLAKE8 := flake8 . --exclude=migrations,.venv,node_modules
PYTEST := pytest . -v --ignore=node_modules --cov=. --cov-config=.coveragerc --capture=no $(pytest_args)
COLLECT_STATIC := python manage.py collectstatic --noinput
CODECOV := \
	if [ "$$CODECOV_REPO_TOKEN" != "" ]; then \
	   codecov --token=$$CODECOV_REPO_TOKEN ;\
	fi

test:
	$(COLLECT_STATIC) && $(FLAKE8) && $(PYTEST) && $(CODECOV)

DJANGO_WEBSERVER := \
	python manage.py distributed_migrate; \
	python manage.py runserver 0.0.0.0:$$PORT

django_webserver:
	$(DJANGO_WEBSERVER)

DOCKER_COMPOSE_REMOVE_AND_PULL := docker-compose -f docker-compose.yml -f docker-compose-test.yml rm -f && docker-compose -f docker-compose.yml -f docker-compose-test.yml pull
DOCKER_COMPOSE_CREATE_ENVS := ./docker/create_envs.sh

docker_run:
	$(DOCKER_COMPOSE_CREATE_ENVS) && \
	$(DOCKER_COMPOSE_REMOVE_AND_PULL) && \
	docker-compose up --build

DEBUG_TEST_SET_ENV_VARS := \
	export DIRECTORY_API_EXTERNAL_CLIENT_CLASS_NAME='unit-test'

DOCKER_SET_DEBUG_ENV_VARS := \
	export SSO_PORT=8003; \
	export SSO_DEBUG=true; \
	export SSO_SECRET_KEY=debug; \
	export SSO_POSTGRES_USER=debug; \
	export SSO_POSTGRES_PASSWORD=debug; \
	export SSO_POSTGRES_DB=sso_debug; \
	export SSO_DATABASE_URL=postgres://debug:debug@postgres:5432/sso_debug; \
	export SSO_SESSION_COOKIE_DOMAIN=.trade.great; \
	export SSO_SSO_SESSION_COOKIE=debug_sso_session_cookie; \
	export SSO_CSRF_COOKIE_SECURE=false; \
	export SSO_SESSION_COOKIE_SECURE=false; \
	export SSO_EMAIL_HOST=debug; \
	export SSO_EMAIL_PORT=debug; \
	export SSO_EMAIL_HOST_USER=debug; \
	export SSO_EMAIL_HOST_PASSWORD=debug; \
	export SSO_DEFAULT_FROM_EMAIL=debug; \
	export SSO_LOGOUT_REDIRECT_URL=http://buyer.trade.great:8001; \
	export SSO_REDIRECT_FIELD_NAME=next; \
	export SSO_ALLOWED_REDIRECT_DOMAINS=example.com,exportingisgreat.gov.uk,great; \
	export SSO_UTM_COOKIE_DOMAIN=.great; \
	export SSO_GOOGLE_TAG_MANAGER_ID=GTM-5K54QJ; \
	export SSO_SIGNATURE_SECRET=signature_secret_debug; \
	export SSO_DEFAULT_REDIRECT_URL=http://buyer.trade.great:8001; \
	export SSO_SSO_PROFILE_URL=http://profile.trade.great:8006; \
	export SSO_DIRECTORY_API_EXTERNAL_CLIENT_BASE_URL=http://buyer.trade.great:8001/api/external/; \
	export SSO_DIRECTORY_API_EXTERNAL_SIGNATURE_SECRET=debug; \
	export SSO_EXOPS_APPLICATION_CLIENT_ID=debug; \
	export SSO_CACHE_BACKEND=locmem; \
	export SSO_PYTHONWARNINGS=all; \
	export SSO_PYTHONDEBUG=true; \
	export SSO_SECURE_SSL_REDIRECT=false; \
	export SSO_HEALTH_CHECK_TOKEN=debug; \
	export SSO_FEATURE_TEST_API_ENABLED=true; \
	export SSO_GOV_NOTIFY_API_KEY=debug; \
	export SSO_HEADER_FOOTER_URLS_GREAT_HOME=http://exred.trade.great:8007/; \
	export SSO_HEADER_FOOTER_URLS_FAB=http://buyer.trade.great:8001; \
	export SSO_HEADER_FOOTER_URLS_SOO=http://soo.trade.great:8008; \
	export SSO_HEADER_FOOTER_URLS_CONTACT_US=http://contact.trade.great:8009/directory/; \
	export SSO_SSO_BASE_URL=http://sso.trade.great:8003 \
	export SSO_ACTIVITY_STREAM_IP_WHITELIST=1.2.3.4 \
	export SSO_ACTIVITY_STREAM_ACCESS_KEY_ID=some-id \
	export SSO_ACTIVITY_STREAM_SECRET_ACCESS_KEY=some-secret \
	export SSO_FEATURE_ACTIVITY_STREAM_NONCE_CACHE_ENABLED=true \
	export SSO_VCAP_SERVICES="{\"redis\": [{\"credentials\": {\"uri\": \"http://redis_cluster:7000/\"}}]}"

docker_test_env_files:
	$(DOCKER_SET_DEBUG_ENV_VARS) && \
	$(DOCKER_COMPOSE_CREATE_ENVS)

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
	docker-compose run webserver python manage.py distributed_migrate && \
	docker-compose run webserver python manage.py loaddata fixtures/development.json && \
	docker-compose run --service-ports webserver make django_webserver

docker_webserver_bash:
	docker exec -it sso_webserver_1 sh

docker_psql:
	docker-compose run postgres psql -h postgres -U debug

docker_test: docker_remove_all
	$(DOCKER_SET_DEBUG_ENV_VARS) && \
	$(DEBUG_TEST_SET_ENV_VARS) && \
	$(DOCKER_COMPOSE_CREATE_ENVS) && \
	$(DOCKER_COMPOSE_REMOVE_AND_PULL) && \
	docker-compose -f docker-compose-test.yml build && \
	docker-compose -f docker-compose-test.yml run sut

DEBUG_SET_ENV_VARS := \
	export SECRET_KEY=debug; \
	export SIGNATURE_SECRET=api_signature_debug; \
	export PORT=8003; \
	export DEBUG=true; \
	export DB_NAME=sso_debug; \
	export DB_USER=debug; \
	export DB_PASSWORD=debug; \
	export DATABASE_URL=postgres://debug:debug@localhost:5432/sso_debug; \
	export SESSION_COOKIE_DOMAIN=.trade.great; \
	export SESSION_COOKIE_SECURE=false; \
	export CSRF_COOKIE_SECURE=false; \
	export SSO_SESSION_COOKIE=debug_sso_session_cookie; \
	export EMAIL_HOST=debug; \
	export EMAIL_PORT=debug; \
	export EMAIL_HOST_USER=debug; \
	export EMAIL_HOST_PASSWORD=debug; \
	export DEFAULT_FROM_EMAIL=debug; \
	export LOGOUT_REDIRECT_URL=http://buyer.trade.great:8001; \
	export REDIRECT_FIELD_NAME=next; \
	export ALLOWED_REDIRECT_DOMAINS=example.com,exportingisgreat.gov.uk,great; \
	export UTM_COOKIE_DOMAIN=.great; \
	export GOOGLE_TAG_MANAGER_ID=GTM-5K54QJ; \
	export SSO_PROFILE_URL=http://profile.trade.great:8006; \
	export EMAIL_BACKEND_CLASS_NAME=console; \
	export DEFAULT_REDIRECT_URL=http://buyer.trade.great:8001; \
	export DIRECTORY_API_EXTERNAL_CLIENT_BASE_URL=http://buyer.trade.great:8001/api/external/; \
	export DIRECTORY_API_EXTERNAL_SIGNATURE_SECRET=debug; \
	export EXOPS_APPLICATION_CLIENT_ID=debug; \
	export CACHE_BACKEND=locmem; \
	export PYTHONWARNINGS=all; \
	export PYTHONDEBUG=true; \
	export SECURE_SSL_REDIRECT=false; \
	export HEALTH_CHECK_TOKEN=debug; \
	export FEATURE_TEST_API_ENABLED=true; \
	export GOV_NOTIFY_API_KEY=debug; \
	export HEADER_FOOTER_URLS_GREAT_HOME=http://exred.trade.great:8007/; \
	export HEADER_FOOTER_URLS_FAB=http://buyer.trade.great:8001; \
	export HEADER_FOOTER_URLS_SOO=http://soo.trade.great:8008; \
	export HEADER_FOOTER_URLS_CONTACT_US=http://contact.trade.great:8009/directory/; \
	export SSO_BASE_URL=http://sso.trade.great:8003 \
	export ACTIVITY_STREAM_IP_WHITELIST=1.2.3.4 \
	export ACTIVITY_STREAM_ACCESS_KEY_ID=some-id \
	export ACTIVITY_STREAM_SECRET_ACCESS_KEY=some-secret; \
	export FEATURE_ACTIVITY_STREAM_NONCE_CACHE_ENABLED=true \
	export VCAP_SERVICES="{\"redis\": [{\"credentials\": {\"uri\": \"http://redis_cluster:7000/\"}}]}"

debug_webserver:
	 $(DEBUG_SET_ENV_VARS)&& $(COLLECT_STATIC) && $(DJANGO_WEBSERVER);

debug_shell:
	 $(DEBUG_SET_ENV_VARS); ./manage.py shell

DEBUG_CREATE_DB := \
	psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$$DB_NAME'" | \
	grep -q 1 || psql -U postgres -c "CREATE DATABASE $$DB_NAME"; \
	psql -U postgres -tc "SELECT 1 FROM pg_roles WHERE rolname = '$$DB_USER'" | \
	grep -q 1 || echo "CREATE USER $$DB_USER WITH PASSWORD '$$DB_PASSWORD'; GRANT ALL PRIVILEGES ON DATABASE \"$$DB_NAME\" to $$DB_USER; ALTER USER $$DB_USER CREATEDB" | psql -U postgres

debug_db:
	$(DEBUG_SET_ENV_VARS) && $(DEBUG_CREATE_DB)

debug_test:
	$(DEBUG_SET_ENV_VARS) && $(COLLECT_STATIC) && $(PYTEST)

debug_test_last_failed:
	make debug_test pytest_args='-v --last-failed'

debug_manage:
	$(DEBUG_SET_ENV_VARS) && ./manage.py $(cmd)

debug: test_requirements debug_db debug_test

dumpdata:
	$(DEBUG_SET_ENV_VARS) $(printf "\033c") && ./manage.py dumpdata --all --indent=4> fixtures/development.json

loaddata:
	$(DEBUG_SET_ENV_VARS) && ./manage.py loaddata fixtures/development.json

migrations:
	$(DEBUG_SET_ENV_VARS) && ./manage.py makemigrations user oauth2

integration_tests:
	cd $(mktemp -d) && \
	git clone https://github.com/uktrade/directory-tests && \
	cd directory-tests && \
	make docker_integration_tests

heroku_deploy_dev:
	./docker/install_heroku_cli.sh
	docker login --username=$$HEROKU_EMAIL --password=$$HEROKU_TOKEN registry.heroku.com
	~/bin/heroku-cli/bin/heroku container:push web --app directory-sso-dev
	~/bin/heroku-cli/bin/heroku container:release web --app directory-sso-dev

compile_requirements:
	pip-compile requirements.in
	pip-compile requirements_test.in

upgrade_requirements:
	pip-compile --upgrade requirements.in
	pip-compile --upgrade requirements_test.in

.PHONY: build clean test_requirements docker_test docker_run docker_debug docker_webserver_bash docker_psql docker_test debug_webserver debug_db debug_test debug migrations heroku_deploy_dev
