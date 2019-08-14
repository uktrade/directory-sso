clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

test_requirements:
	pip install -r requirements_test.txt

FLAKE8 := flake8 . --exclude=migrations,.venv,node_modules --max-line-length=120
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

DEBUG_TEST_SET_ENV_VARS := \
	export DEBUG=False

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
	export UTM_COOKIE_DOMAIN=.trade.great; \
	export GOOGLE_TAG_MANAGER_ID=GTM-5K54QJ; \
	export SSO_PROFILE_URL=http://profile.trade.great:8006; \
	export EMAIL_BACKEND_CLASS_NAME=console; \
	export DEFAULT_REDIRECT_URL=http://profile.trade.great:8006/profile/ \
	export DIRECTORY_API_EXTERNAL_CLIENT_BASE_URL=http://buyer.trade.great:8001/api/external/; \
	export DIRECTORY_API_EXTERNAL_SIGNATURE_SECRET=debug; \
	export EXOPS_APPLICATION_CLIENT_ID=debug; \
	export CACHE_BACKEND=locmem; \
	export SECURE_SSL_REDIRECT=false; \
	export HEALTH_CHECK_TOKEN=debug; \
	export FEATURE_TEST_API_ENABLED=true; \
	export GOV_NOTIFY_API_KEY=debug; \
	export SSO_BASE_URL=http://sso.trade.great:8003; \
	export ACTIVITY_STREAM_IP_WHITELIST=1.2.3.4; \
	export ACTIVITY_STREAM_ACCESS_KEY_ID=some-id; \
	export ACTIVITY_STREAM_SECRET_ACCESS_KEY=some-secret; \
	export FEATURE_ACTIVITY_STREAM_NONCE_CACHE_ENABLED=true; \
	export VCAP_SERVICES="{\"redis\": [{\"credentials\": {\"uri\": \"redis://127.0.0.1:7000/\"}}]}"; \
	export PRIVACY_COOKIE_DOMAIN=.trade.great; \
	export SESSION_COOKIES_NAME_DOMAIN_MAPPING="debug_sso_session_cookie=.trade.great"; \
	export DIRECTORY_CONSTANTS_URL_GREAT_DOMESTIC=http://exred.trade.great:8007; \
	export DIRECTORY_CONSTANTS_URL_FIND_A_BUYER=http://buyer.trade.great:8001; \
	export DIRECTORY_CONSTANTS_URL_SELLING_ONLINE_OVERSEAS=http://soo.trade.great:8008; \
	export DIRECTORY_CONSTANTS_URL_FIND_A_SUPPLIER=http://supplier.trade.great:8005; \
	export DIRECTORY_CONSTANTS_URL_INVEST=http://invest.trade.great:8012; \
	export DIRECTORY_CONSTANTS_URL_SINGLE_SIGN_ON=http://sso.trade.great:8004; \
	export DIRECTORY_CONSTANTS_URL_SSO_PROFILE=http://profile.trade.great:8006/profile/; \
	export FEATURE_NEW_ENROLMENT_ENABLED=true

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

compile_requirements:
	pip-compile requirements.in
	pip-compile requirements_test.in

upgrade_requirements:
	pip-compile --upgrade requirements.in
	pip-compile --upgrade requirements_test.in

compile_css:
	./node_modules/.bin/gulp sass

watch_css:
	./node_modules/.bin/gulp sass:watch

.PHONY: build clean test_requirements debug_webserver debug_db debug_test debug migrations heroku_deploy_dev
