# directory-sso

[![code-climate-image]][code-climate]
[![circle-ci-image]][circle-ci]
[![codecov-image]][codecov]
[![gitflow-image]][gitflow]
[![calver-image]][calver]

---

**Service for authenticating users for services that serve the Exporting is Great campaign for the Department for International Trade (DIT).**

## Development

### Installing

    $ git clone https://github.com/uktrade/directory-sso
    $ cd directory-sso
    $ virtualenv .venv -p python3.6
    $ source .venv/bin/activate
    $ pip install -r requirements_text.txt


### Requirements
[Python 3.6](https://www.python.org/downloads/release/python-366/)

[Postgres](https://www.postgresql.org/)

### Configuration

Secrets such as API keys and environment specific configurations are placed in `conf/.env` - a file that is not added to version control. You will need to create that file locally in order for the project to run.

### Development data

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


### Run the webserver

    $ make debug_webserver

### Run the tests

    $ make debug_test

### CSS development

If you're doing front-end development work you will need to be able to compile the SASS to CSS. For this you need:

### Requirements

[node](https://nodejs.org/en/download/)
[SASS](https://rubygems.org/gems/sass/versions/3.4.22)

    $ npm install yarn
    $ yarn install --production=false

### Compiling

We add compiled CSS files to version control. This will sometimes result in conflicts if multiple developers are working on the same SASS files. However, by adding the compiled CSS to version control we avoid having to install node, npm, node-sass, etc to non-development machines.

You should not edit CSS files directly, instead edit their SCSS counterparts.

### Update CSS under version control

    $ make compile_css

### Rebuild the CSS files when the scss file changes

    $ make watch_css

## Helpful links
* [Developers Onboarding Checklist](https://uktrade.atlassian.net/wiki/spaces/ED/pages/32243946/Developers+onboarding+checklist)
* [Gitflow branching](https://uktrade.atlassian.net/wiki/spaces/ED/pages/737182153/Gitflow+and+releases)
* [GDS service standards](https://www.gov.uk/service-manual/service-standard)
* [GDS design principles](https://www.gov.uk/design-principles)

## Related projects:
https://github.com/uktrade?q=directory
https://github.com/uktrade?q=great


[code-climate-image]: https://codeclimate.com/github/uktrade/directory-sso/badges/issue_count.svg
[code-climate]: https://codeclimate.com/github/uktrade/directory-sso

[code-climate-image]: https://codeclimate.com/github/uktrade/directory-sso/badges/issue_count.svg
[code-climate]: https://codeclimate.com/github/uktrade/directory-sso

[circle-ci-image]: https://circleci.com/gh/uktrade/directory-sso/tree/master.svg?style=svg
[circle-ci]: https://circleci.com/gh/uktrade/directory-sso/tree/master

[codecov-image]: https://codecov.io/gh/uktrade/directory-sso/branch/master/graph/badge.svg
[codecov]: https://codecov.io/gh/uktrade/directory-sso
