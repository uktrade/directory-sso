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
    $ [create virtual environment]
    $ source .venv/bin/activate
    $ make requirements

### Getting started

    $ createdb sso_debug
    $ make manage migrate
    $ make manage loaddata fixtures/development.json
    $ make webserver  

### Requirements
[Python 3.6](https://www.python.org/downloads/release/python-366/)

[Postgres](https://www.postgresql.org/)

### Configuration

Secrets such as API keys and environment specific configurations are placed in `conf/env/secrets-do-not-commit` - a file that is not added to version control. To create a template secrets file with dummy values run `make secrets`.

### Commands

| Command                       | Description |
| ----------------------------- | ------------|
| make clean                    | Delete pyc files |
| make pytest                   | Run all tests |
| make pytest test_foo.py       | Run all tests in file called test_foo.py |
| make pytest -- --last-failed` | Run the last tests to fail |
| make pytest -- -k foo         | Run the test called foo |
| make pytest -- <foo>          | Run arbitrary pytest command |
| make manage <foo>             | Run arbitrary management command |
| make webserver                | Run the development web server |
| make requirements             | Compile the requirements file |
| make install_requirements     | Installed the compile requirements file |
| make css                      | Compile scss to css |
| make secrets                  | Create your secret env var file |
| make flake8                   | Run flake8 linting |
| make checks                   | Run black, isort, flake8 in check mode |
| make autoformat               | Run black and isort in file-writing mode |

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

### Testing
We are using distributed testing by default. You can disable it by removing `-n auto --dist=loadfile ` from the pytest.ini 
You can also disable it by running pytest with `--dist=no --pdb` and insert a breaking assertion (e.g. `assert 0`) where you would normally `pdb.set_trace()`.

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

[circle-ci-image]: https://circleci.com/gh/uktrade/directory-sso/tree/master.svg?style=svg
[circle-ci]: https://circleci.com/gh/uktrade/directory-sso/tree/master

[codecov-image]: https://codecov.io/gh/uktrade/directory-sso/branch/master/graph/badge.svg
[codecov]: https://codecov.io/gh/uktrade/directory-sso

[gitflow-image]: https://img.shields.io/badge/Branching%20strategy-gitflow-5FBB1C.svg
[gitflow]: https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow

[calver-image]: https://img.shields.io/badge/Versioning%20strategy-CalVer-5FBB1C.svg
[calver]: https://calver.org
