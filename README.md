# sso

## Build status

[![CircleCI](https://circleci.com/gh/uktrade/sso/tree/master.svg?style=svg)](https://circleci.com/gh/uktrade/sso/tree/master)

## Requirements
[Docker >= 1.10](https://docs.docker.com/engine/installation/)

[Docker Compose >= 1.8](https://docs.docker.com/compose/install/)

## Local installation

    $ git clone https://github.com/uktrade/sso
    $ cd sso
    $ make

## Running with Docker
Requires all host environment variables to be set.

    $ make docker_run

### Run debug webserver in Docker
Provides defaults for all environment variables.

    $ make docker_debug

### Run tests in Docker

    $ make docker_test

### Host environment variables for docker-compose
``.env`` files will be automatically created with ``env_writer.py``, based on ``env.json`` and ``env-postgres.json``.

#### Web server and queue worker
| Host environment variable | Docker environment variable  |
| ------------- | ------------- |
| SSO_SECRET_KEY | SECRET_KEY |
| SSO_DATABASE_URL | DATABASE_URL |
| SSO_LOGOUT_REDIRECT_URL | LOGOUT_REDIRECT_URL |

#### Database
| Host environment variable | Docker environment variable  |
| ------------- | ------------- |
| SSO_POSTGRES_USER | POSTGRES_USER |
| SSO_POSTGRES_PASSWORD | POSTGRES_PASSWORD |
| SSO_POSTGRES_DB | POSTGRES_DB |

## Debugging

### Setup debug environment
Requires locally running PostgreSQL (e.g. [Postgres.app](http://postgresapp.com/) for the Mac)
    
    $ make debug

### Run debug webserver

    $ make debug_webserver

### Run debug tests

    $ make debug_test


## Environment variables

| Environment variable | Default value | Description 
| ------------- | ------------- | ------------- |
| SECRET_KEY | None | Django secret key |
| DATABASE_URL | None | Postgres database url |
| LOGOUT_REDIRECT_URL | None | Where to send the user after successfully logging out |
