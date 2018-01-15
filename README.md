# directory-sso

[![code-climate-image]][code-climate]
[![circle-ci-image]][circle-ci]
[![codecov-image]][codecov]
[![gemnasium-image]][gemnasium]

---

**Service for authenticating users for services that serve the Exporting is Great campaign for the Department for International Trade (DIT).**

### See also:
| [directory-api](https://github.com/uktrade/directory-api) | [directory-ui-buyer](https://github.com/uktrade/directory-ui-buyer) | [directory-ui-supplier](https://github.com/uktrade/directory-ui-supplier) | [directory-ui-export-readiness](https://github.com/uktrade/directory-ui-export-readiness) |
| --- | --- | --- | --- |
| **[directory-sso](https://github.com/uktrade/directory-sso)** | **[directory-sso-proxy](https://github.com/uktrade/directory-sso-proxy)** | **[directory-sso-profile](https://github.com/uktrade/directory-sso-profile)** |  |

For more information on installation please check the [Developers Onboarding Checklist](https://uktrade.atlassian.net/wiki/spaces/ED/pages/32243946/Developers+onboarding+checklist)

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

## Running locally without Docker

### Installing

```bash
$ git clone https://github.com/uktrade/directory-sso
$ cd directory-sso
$ virtualenv .venv -p python3.5
$ source .venv/bin/activate
$ pip install -r requirements_text.txt
```

### Running the webserver

```bash
$ source .venv/bin/activate
$ make debug_webserver
```

### Running the tests

```bash
$ make debug_test
```

## Debugging

### Setup debug environment
Requires locally running PostgreSQL (e.g. [Postgres.app](http://postgresapp.com/) for the Mac)

    $ make debug

### Run debug webserver

    $ make debug_webserver

### Run debug tests

    $ make debug_test

## Development data

For development efficiency a dummy user can be loaded into the database from `fixtures/development.json`. To do this run:

```bash
make loaddata
```

The credentials for the development user `dev@example.com`:`password`.

To update `fixtures/development.json` with the current contents of the database run:

```bash
make dumpdata
```

Then check the contents of `fixtures/development.json`.

## CSS development

If you're doing front-end development work you will need to be able to compile the SASS to CSS. For this you need:

	$ npm install
	$ gulp

We add compiled CSS files to version control. This will sometimes result in conflicts if multiple developers are working on the same SASS files. However, by adding the compiled CSS to version control we avoid having to install node, npm, node-sass, etc to non-development machines.

You should not edit CSS files directly, instead edit their SCSS counterparts.

[code-climate-image]: https://codeclimate.com/github/uktrade/directory-sso/badges/issue_count.svg
[code-climate]: https://codeclimate.com/github/uktrade/directory-sso

[circle-ci-image]: https://circleci.com/gh/uktrade/directory-sso/tree/master.svg?style=svg
[circle-ci]: https://circleci.com/gh/uktrade/directory-sso/tree/master

[codecov-image]: https://codecov.io/gh/uktrade/directory-sso/branch/master/graph/badge.svg
[codecov]: https://codecov.io/gh/uktrade/directory-sso

[gemnasium-image]: https://gemnasium.com/badges/github.com/uktrade/directory-sso.svg
[gemnasium]: https://gemnasium.com/github.com/uktrade/directory-sso
