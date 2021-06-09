# Changelog

## Pre release

### Enhancements
- no-ticket - dependencies upgrade

### Fixed bugs
- NOTICKET - Refactor GOV notification response

## [8.0.0](https://github.com/uktrade/directory-sso/releases/tag/8.0.0)
[Compare](https://github.com/uktrade/directory-sso/compare/6.6.0...8.0.0)

- GP2-2380 - Bump directory-components
- GP2-2327 - Expose social login attribute
- GP2-2225 - forgotten password notification social accounts
- NOTICKET - Remove social provider in settings confusing as it's stored in django admin
- GP2-2554 - error-page-update-links
### Fixed bugs


## [6.6.0](https://github.com/uktrade/directory-sso/releases/tag/6.6.0)
[Compare](https://github.com/uktrade/directory-sso/compare/6.5.0...6.6.0)

### Enhancements
- GP2-2135 - User data storage
- GP2-2388 - Added field for Data retention admin UI
- GP2-2381 - Updated contact link in footer via upgrading directory-component
- GP2-2353 - VFM final page back button
- GP2-2256 - magna header for BAU pages
- GP2-2332 - upgraded directory-components package
- NOTICKET -  upgrade python 3.9.2


## [v6.5.1](https://github.com/uktrade/directory-sso/releases/tag/v6.5.1)
[Compare](https://github.com/uktrade/directory-sso/compare/6.5.0...6.5.1)
## Enhancements
- No ticket - Python version bump to 2.9.2


## [v6.5.0](https://github.com/uktrade/directory-sso/releases/tag/v6.5.0)
[Compare](https://github.com/uktrade/directory-sso/compare/6.4.0...6.5.0)
## Enhancements
- GBAU-949 - Password reset page failing
- GP2-2176 - Value for Money Questions

## [6.4.0](https://github.com/uktrade/directory-sso/releases/tag/6.4.0)
[Compare](https://github.com/uktrade/directory-sso/compare/6.3.0...6.4.0)
### Enhancements
- No ticket - Upgraded cryptography package
- No ticket - update Activity Steam endpoint to deny requests from public network

## [6.3.0](https://github.com/uktrade/directory-sso/releases/tag/6.3.0)
[Compare](https://github.com/uktrade/directory-sso/compare/6.2.0...6.3.0)
### Enhancements
- GP2-1722 - Data retention statistics model
- GP2-1720 -  Added final check for notification before archive users
- No ticket - Upgraded cryptography package
- No ticket - update Activity Steam endpoint to deny requests from public network

## [6.2.0](https://github.com/uktrade/directory-sso/releases/tag/6.2.0)
[Compare](https://github.com/uktrade/directory-sso/compare/6.1.0...6.2.0)

### Implemented enhancements
-   GP2-1719 - Add segmentation to profile
-   GP2-1721 - Added script to notifying user for deletion as per data retention policy
-   GP2-1068 - adopt Black auto-formatting + provide optional pre-commit config
-   No ticket - added Activity Stream endpoint to list users

## [6.1.0](https://github.com/uktrade/directory-sso/releases/tag/6.1.0)
### Fixed bugs:

- GBAU-869 - Terminate session on logout from outside SSO

### Implemented enhancements
- GP2-1068 - adopt Black auto-formatting + provide optional pre-commit config

## [6.0.0](https://github.com/uktrade/directory-sso/releases/tag/6.0.0)

[Full Changelog](https://github.com/uktrade/directory-sso/compare/6.0.0)

### Fixed bugs:

-   GAA-27 - directory-components version bump
-   No ticket - Lesson completed delete fix
-   No ticket - no profile linked in pic key error

### Implemented enhancements

-   GP2-763 - Add social auth to profile
-   GBAU-217 - data retention: added management command to archive users
-   GP2-36 - Lesson completed model
-   GP2-238 - page visit model

## [2020.07.09](https://github.com/uktrade/directory-sso/releases/tag/2020.07.09)

[Full Changelog](https://github.com/uktrade/directory-sso/compare/2020.04.30...2020.07.09)

### Implemented enhancements

-   GP2-94 - Send welcome email on social login
-   TT-2332- remove old sso sign-up

## [2020.04.30](https://github.com/uktrade/directory-sso/releases/tag/2020.04.30)

[Full Changelog](https://github.com/uktrade/directory-sso/compare/2020.02.11...2020.04.30)

### Implemented enhancements

-   TT-2285 - Add an option to create test users via testapi
-   no ticket - Create user profile on social signup
-   MVP-295 - Expose social profile image
-   no ticket - replace test Factories in TestAPI views with regular models
-   AA-115 - Update tests to use correct test email domain

### Fixed bugs:

-   No ticket - Prevent embedding in an iframe
-   No ticket - upgrade Pillow to fix security vulnerability
-   No ticket - v3-cipipeline manifest.yml file fix
-   TT-2254 - Cleaned up obsolete settings

## [2020.02.11](https://github.com/uktrade/directory-ssoreleases/tag/2020.02.11)

[Full Changelog](https://github.com/uktrade/directory-sso/compare/2020.01.14_2...2020.02.11)

### Hotfix

-   XOT-1296 - replace cookie banner with cookie modal

## [2020.01.14_2](https://github.com/uktrade/directory-sso/releases/tag/2020.01.14_2)

[Full Changelog](https://github.com/uktrade/directory-sso/compare/2020.01.14...2020.01.14_2)

### Hotfix

-   No ticket - CVE-2020-5236 & CVE-2020-7471: Potential SQL injection via StringAgg(delimiter)

## [2020.01.14](https://github.com/uktrade/directory-sso/releases/tag/2020.01.14)

[Full Changelog](https://github.com/uktrade/directory-sso/compare/2019.12.18_1...2020.01.14)

### Implemented enhancements

-   TT-2234 - upgrade staff sso foruser id
-   TT-2248 - Facilitate .internal domain communication

### Fixed bugs

-   TT-1096 - redirect to resend verification code if not provided code
-   TT-1614 - set secure flag on sso_display_logged_in

## [2019.12.18](https://github.com/uktrade/directory-sso/releases/tag/2019.12.18_1)

[Full Changelog](https://github.com/uktrade/directory-sso/compare/2019.10.30...2019.12.18_1)

### Implemented enhancements

-   GTRANSFORM-385 - Business sso response to include first/last name
-   TT-1798 implement-staff-sso
-   TT-2197 Add testapi endpoint to SSO to delete users created by automated tests
-   No ticket - Upgrade Django
-   TT-2188 - Add GDRP admin filter
-   TT-1304 - Upgrade sentry client

## [2019.10.30](https://github.com/uktrade/directory-sso/releases/tag/.2019.10.30)

[Full Changelog](https://github.com/uktrade/directory-sso/compare/2019.08.13_1....2019.10.30)

### Implemented enhancements

-   TT-1080 - Login user automatically after password reset
-   No ticket - Added django settings janitor
-   Expose user profile on user retrieve endpoint
-   TT-1673 - Redirect to enrolment after login if no company or personal details
-   TT-1760 - added user profile update
-   TT-1808: Update directory components to add "no-validate" no cache middleware

### Fixed bugs:

-   No ticket - Upgrade django to 1.11.23 for vulnerability fix
-   No ticket - Fix vulnerability with yarn
-   No ticket - Cleared up old settings
-   TT-1758 - Fix breadcrumbs on change password page
-   TT-1779 - Fix login hanging
-   TT-1614 - CRSF httponly
-   TT-1834 - Fix bad spacing on login page
-   TT-1823 - Send unverified users to verification page on login
-   TT-1952 - Removing loop for individual users to select business type on login
-   TT-1927 - Fix duplicate error messages on login page

## [2019.08.13](https://github.com/uktrade/directory-sso/releases/tag/2019.08.13_1)

[Full Changelog](https://github.com/uktrade/directory-sso/compare/2019.08.13...2019.08.13_1)

### Hot fix

-   No ticket - Add feature flag to "start now" on sign in page

## [2019.08.13](https://github.com/uktrade/directory-sso/releases/tag/2019.08.13)

[Full Changelog](https://github.com/uktrade/directory-sso/compare/2019.07.09...2019.08.13)

### Implemented enhancements

-   No Ticket - Adding missing models to admin view
-   TT-990 - Making job title optional in user profile to accomodate individual user profile.
-   TT-1573 - Expose has_user_profile on session user retrieval
-   No ticket - Send user to SSO profile enrolment instead of SSO register page

## [2019.07.09](https://github.com/uktrade/directory-sso/releases/tag/2019.07.09)

[Full Changelog](https://github.com/uktrade/directory-sso/compare/2019.06.27...2019.07.09)

### Fixed bugs:

-   No ticket - Upgrade vulnerable django version to django 1.11.22

## [2019.06.27](https://github.com/uktrade/directory-sso/releases/tag/2019.06.27)

[Full Changelog](https://github.com/uktrade/directory-sso/compare/2019.04.11...2019.06.27)

### Implemented enhancements

-   GTRANSFORM-245 - UserID Anonymisation extension for GA360

### Fixed bugs:

-   TT-1556 incorrect use of ul lists
-   [[TT-1353]](https://uktrade.atlassian.net/browse/TT-1353) - Prevent attempting to create multiple user profiles for the same user
-   Upgraded urllib3 to fix [vulnerability](https://nvd.nist.gov/vuln/detail/CVE-2019-11324)
-   Prevent already encrypted password being re-encrypted when user is saved in admin.
-   Upgrade django-restframework to 3.9.1 to fix XSS vulnerability
-   no ticket - fix the page title on sign in
-   no ticket - upgrade django to fix security vulnerability
-   no ticket - upgrade django rest framework to fix security vulnerability
