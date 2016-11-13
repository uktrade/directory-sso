# directory-sso

## Build status

[![CircleCI](https://circleci.com/gh/uktrade/directory-sso/tree/master.svg?style=svg)](https://circleci.com/gh/uktrade/directory-sso/tree/master)

## Requirements
[Docker >= 1.10](https://docs.docker.com/engine/installation/)

[Docker Compose >= 1.8](https://docs.docker.com/compose/install/)

## Local installation

    $ git clone https://github.com/uktrade/directory-sso
    $ cd directory-sso
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


## Debugging

### Setup debug environment
Requires locally running PostgreSQL (e.g. [Postgres.app](http://postgresapp.com/) for the Mac)

    $ make debug

### Run debug webserver

    $ make debug_webserver

### Run debug tests

    $ make debug_test
