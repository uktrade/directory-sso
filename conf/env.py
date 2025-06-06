from typing import Any, Optional

from dbt_copilot_python.database import database_url_from_env
from dbt_copilot_python.utility import is_copilot
from pydantic import BaseModel, ConfigDict, Field, computed_field
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import SettingsConfigDict

from conf.helpers import get_env_files, is_circleci, is_local


class BaseSettings(PydanticBaseSettings):
    """Base class holding all environment variables for Great."""

    model_config = SettingsConfigDict(
        extra="ignore",
        validate_default=False,
    )

    # Start of Environment Variables
    debug: bool = False
    app_environment: str = "dev"
    static_host: str = ""
    staticfiles_storage: str = "whitenoise.storage.CompressedStaticFilesStorage"
    secret_key: str
    sentry_dsn: str = ""
    sentry_environment: str = ""
    sentry_enable_tracing: bool = False
    sentry_traces_sample_rate: float = 1.0

    allowed_ips: str = ''

    feature_enforce_staff_sso_enabled: bool = False

    staff_sso_authbroker_url: str
    authbroker_client_id: str
    authbroker_client_secret: str

    rest_framework_page_size: int = 1000

    redirect_field_name: str = "next"
    default_redirect_url: str
    logout_redirect_url: str

    account_email_subject_prefix: str = "Your great.gov.uk account: "
    account_default_http_protocol: str = "https"

    verification_expiry_minutes: int = 30

    email_backend_class_name: str = "default"

    email_host: str
    email_port: str
    email_host_user: str
    email_host_password: str
    default_from_email: str

    session_cookie_domain: str = ""
    session_cookie_secure: bool = True
    sso_session_cookie: str

    is_docker: bool = False

    csrf_cookie_secure: bool = True

    csrf_trusted_origins: str = Field(default=[])

    allowed_redirect_domains: str = Field(default=[])

    signature_secret: str

    directory_api_secret: str = ""

    utm_cookie_domain: str
    google_tag_manager_id: str
    google_tag_manager_env: str = ""

    sso_profile_url: str

    magna_url: str

    directory_api_client_base_url: str
    directory_api_client_api_key: str
    directory_api_client_sender_id: str = "directory"
    directory_api_client_default_timeout: int = 15

    directory_forms_api_base_url: str
    directory_forms_api_api_key: str
    directory_forms_api_sender_id: str
    directory_forms_api_default_timeout: int = 5
    directory_forms_api_zendesk_sevice_name: str = "api"

    exops_application_client_id: str
    directory_constants_url_great_domestic: str = ""
    directory_constants_url_export_opportunities: str = ""
    directory_constants_url_selling_online_overseas: str = ""
    directory_constants_url_events: str = ""
    directory_constants_url_invest: str = ""
    directory_constants_url_find_a_supplier: str = ""
    directory_constants_url_single_sign_on: str = ""
    directory_constants_url_find_a_buyer: str = ""
    directory_constants_url_sso_profile: str = ""
    privacy_cookie_domain: str

    sso_suspicious_login_max_attempts: int = 10
    sso_suspicious_activity_notification_email: str = ""

    health_check_token: str

    gov_notify_api_key: str
    gov_notify_signup_confirmation_template_id: str = "0c76b730-ac37-4b08-a8ba-7b34e4492853"
    bgs_gov_notify_signup_confirmation_template_id: str = "727f7eeb-59a9-4772-854b-c2f2d92d0c65"
    gov_notify_password_reset_template_id: str = "9ef82687-4bc0-4278-b15c-a49bc9325b28"
    bgs_gov_notify_password_reset_template_id: str = "1b0f8925-d027-4034-9bae-c276b6fef3f2"
    gov_notify_password_reset_unverified_template_id: str = "6ad90342-6e55-4026-8884-b8a1d4d7f11c"
    bgs_gov_notify_password_reset_unverified_template_id: str = "a7e3c98c-1f0b-4c22-a44f-a95268d3d58d"
    gov_notify_social_password_reset_template_id: str = "e5b5416d-854b-4aef-82da-865b6f901dbd"
    gov_notify_already_registered_template_id: str = "5c8cc5aa-a4f5-48ae-89e6-df5572c317ec"
    gov_notify_welcome_template_id: str = "0a4ae7a9-7f67-4f5d-a536-54df2dee42df"
    gov_notify_data_retention_notification_template_id: str = "39e44eaa-515f-4843-b7c5-d3dd5d86747c"
    bgs_gov_notify_data_retention_notification_template_id: str = "a94de81e-a24a-4c70-9392-b64e98673b58"

    sso_base_url: str = "https://sso.trade.great.gov.uk"

    activity_stream_ip_whitelist: str = ""
    activity_stream_access_key_id: str
    activity_stream_secret_access_key: str

    feature_skip_migrate: bool = False
    feature_disable_registration: bool = False
    feature_test_api_enabled: bool = False
    test_api_email_domain: str = "ci.uktrade.io"
    feature_maintenance_mode_enabled: bool = False

    ip_restrictor_allowed_admin_ips: str = Field(default=[])
    ip_restrictor_restrict_ips: bool = False
    ip_restrictor_allowed_admin_ip_ranges: str = Field(default=[])

    feature_settings_janitor_enabled: bool = False

    directory_components_vault_domain: str = ""
    directory_components_vault_root_path: str = ""
    directory_components_vault_project: str = ""

    feature_redis_use_ssl: bool = False

    celery_task_always_eager: bool = False

    magna_header: bool = False

    directory_constants_url_great_magna: str = "https://great.gov.uk/"

    data_retention_storage_years: int = 3

    feature_use_bgs_templates: bool = False


class CIEnvironment(BaseSettings):

    database_url: str
    redis_url: str


class DBTPlatformEnvironment(BaseSettings):
    """Class holding all listed environment variables on DBT Platform.

    Instance attributes are matched to environment variables by name (ignoring case).
    e.g. DBTPlatformEnvironment.app_environment loads and validates the APP_ENVIRONMENT environment variable.
    """

    build_step: bool = False
    redis_endpoint: str = ""

    @computed_field(return_type=str)
    @property
    def database_url(self):
        return database_url_from_env("DATABASE_CREDENTIALS")

    @computed_field(return_type=str)
    @property
    def redis_url(self):
        return self.redis_endpoint


class GovPaasEnvironment(BaseSettings):
    """Class holding all listed environment variables on Gov PaaS.

    Instance attributes are matched to environment variables by name (ignoring case).
    e.g. GovPaasSettings.app_environment loads and validates the APP_ENVIRONMENT environment variable.
    """

    class VCAPServices(BaseModel):
        """Config of services bound to the Gov PaaS application"""

        model_config = ConfigDict(extra="ignore")

        postgres: list[dict[str, Any]]
        redis: list[dict[str, Any]]

    class VCAPApplication(BaseModel):
        """Config of the Gov PaaS application"""

        model_config = ConfigDict(extra="ignore")

        application_id: str
        application_name: str
        application_uris: list[str]
        cf_api: str
        limits: dict[str, Any]
        name: str
        organization_id: str
        organization_name: str
        space_id: str
        uris: list[str]

    model_config = ConfigDict(extra="ignore")

    vcap_services: Optional[VCAPServices] = None
    vcap_application: Optional[VCAPApplication] = None

    @computed_field(return_type=str)
    @property
    def database_url(self):
        if self.vcap_services:
            return self.vcap_services.postgres[0]["credentials"]["uri"]

        return "postgres://"

    @computed_field(return_type=str)
    @property
    def redis_url(self):
        if self.vcap_services:
            return self.vcap_services.redis[0]["credentials"]["uri"]

        return "rediss://"


if is_local() or is_circleci():
    # Load environment files in a local or CI environment
    env = CIEnvironment(_env_file=get_env_files(), _env_file_encoding="utf-8")
elif is_copilot():
    # When deployed read values from DBT Platform environment
    env = DBTPlatformEnvironment()
else:
    # When deployed read values from Gov PaaS environment
    env = GovPaasEnvironment()
