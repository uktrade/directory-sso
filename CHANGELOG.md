# Changelog

## Pre release

### Implemented enhancements
- No ticket - Added django settings janitor
- Expose user profile on user retrieve endpoint
- TT-1673 - Redirect to enrolment after login if no company or personal details
- TT-1760 - added user profile update

### Fixed bugs:
- No ticket - Upgrade django to 1.11.23 for vulnerability fix
- No ticket - Fix vulnerability with yarn
- No ticket - Cleared up old settings
- TT-1758 - Fix breadcrumbs on change password page
- TT-1779 - Fix login hanging

## [2019.08.13](https://github.com/uktrade/directory-sso/releases/tag/2019.08.13_1)
[Full Changelog](https://github.com/uktrade/directory-sso/compare/2019.08.13...2019.08.13_1)

### Hot fix
- No ticket - Add feature flag to "start now" on sign in page

## [2019.08.13](https://github.com/uktrade/directory-sso/releases/tag/2019.08.13)
[Full Changelog](https://github.com/uktrade/directory-sso/compare/2019.07.09...2019.08.13)

### Implemented enhancements
- No Ticket - Adding missing models to admin view
- TT-990 -  Making job title optional in user profile to accomodate individual user profile.
- TT-1573 - Expose has_user_profile on session user retrieval
- No ticket - Send user to SSO profile enrolment instead of SSO register page

## [2019.07.09](https://github.com/uktrade/directory-sso/releases/tag/2019.07.09)
[Full Changelog](https://github.com/uktrade/directory-sso/compare/2019.06.27...2019.07.09)

### Fixed bugs:
- No ticket - Upgrade vulnerable django version to django 1.11.22

## [2019.06.27](https://github.com/uktrade/directory-sso/releases/tag/2019.06.27)
[Full Changelog](https://github.com/uktrade/directory-sso/compare/2019.04.11...2019.06.27)

### Implemented enhancements
- GTRANSFORM-245 - UserID Anonymisation extension for GA360

### Fixed bugs:
- TT-1556 incorrect use of ul lists
- [[TT-1353]](https://uktrade.atlassian.net/browse/TT-1353) - Prevent attempting to create multiple user profiles for the same user
- Upgraded urllib3 to fix [vulnerability](https://nvd.nist.gov/vuln/detail/CVE-2019-11324)
- Prevent already encrypted password being re-encrypted when user is saved in admin.
- Upgrade django-restframework to 3.9.1 to fix XSS vulnerability
- no ticket - fix the page title on sign in
- no ticket - upgrade django to fix security vulnerability
- no ticket - upgrade django rest framework to fix security vulnerability

