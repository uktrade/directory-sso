# Changelog

## Pre release

### Fixed bugs
- TT-2254 - Cleaned up obsolete settings
- no ticket - replace test Factories in TestAPI views with regular models

### Implemented enhancements
- TT-2285 - Add an option to create test users via testapi
- no ticket - Create user profile on social signup

### Fixed bugs 

## [2020.02.11](https://github.com/uktrade/great-domestic-ui/releases/tag/2020.02.11)
[Full Changelog](https://github.com/uktrade/great-domestic-ui/compare/2020.01.14_2...2020.02.11)

### Hotfix
- No ticket - Replace cookie banner with modal

## [2020.01.14_2](https://github.com/uktrade/great-domestic-ui/releases/tag/2020.01.14_2)
[Full Changelog](https://github.com/uktrade/great-domestic-ui/compare/2020.01.14...2020.01.14_2)

### Hotfix
- No ticket - CVE-2020-5236 & CVE-2020-7471: Potential SQL injection via StringAgg(delimiter)


## [2020.01.14](https://github.com/uktrade/directory-sso/releases/tag/2020.01.14)
[Full Changelog](https://github.com/uktrade/directory-sso/compare/2019.12.18_1...2020.01.14)

### Implemented enhancements
- TT-2234 - upgrade staff sso foruser id
- TT-2248 - Facilitate .internal domain communication

### Fixed bugs
- TT-1096 - redirect to resend verification code if not provided code
- TT-1614 - set secure flag on sso_display_logged_in

## [2019.12.18](https://github.com/uktrade/directory-sso/releases/tag/2019.12.18_1)
[Full Changelog](https://github.com/uktrade/directory-sso/compare/2019.10.30...2019.12.18_1)

### Implemented enhancements
- GTRANSFORM-385 - Business sso response to include first/last name
- TT-1798 implement-staff-sso
- TT-2197 Add testapi endpoint to SSO to delete users created by automated tests
- No ticket - Upgrade Django
- TT-2188 - Add GDRP admin filter
- TT-1304 - Upgrade sentry client

## [2019.10.30](https://github.com/uktrade/directory-sso/releases/tag/.2019.10.30)
[Full Changelog](https://github.com/uktrade/directory-sso/compare/2019.08.13_1....2019.10.30)

### Implemented enhancements
- TT-1080 - Login user automatically after password reset
- No ticket - Added django settings janitor
- Expose user profile on user retrieve endpoint
- TT-1673 - Redirect to enrolment after login if no company or personal details
- TT-1760 - added user profile update
- TT-1808: Update directory components to add "no-validate" no cache middleware

### Fixed bugs:
- No ticket - Upgrade django to 1.11.23 for vulnerability fix
- No ticket - Fix vulnerability with yarn
- No ticket - Cleared up old settings
- TT-1758 - Fix breadcrumbs on change password page
- TT-1779 - Fix login hanging
- TT-1614 - CRSF httponly
- TT-1834 - Fix bad spacing on login page
- TT-1823 - Send unverified users to verification page on login
- TT-1952 - Removing loop for individual users to select business type on login
- TT-1927 - Fix duplicate error messages on login page

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

