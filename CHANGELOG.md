# Changelog

## Pre-release

- GTRANSFORM-245 - UserID Anonymisation extension for GA360

### Fixed bugs:

- [[TT-1353]](https://uktrade.atlassian.net/browse/TT-1353) - Prevent attempting to create multiple user profiles for the same user
- Upgraded urllib3 to fix [vulnerability](https://nvd.nist.gov/vuln/detail/CVE-2019-11324)
- Prevent already encrypted password being re-encrypted when user is saved in admin.
- Upgrade django-restframework to 3.9.1 to fix XSS vulnerability