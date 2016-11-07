from django.forms import BooleanField, ValidationError
from django.utils.safestring import mark_safe

from allauth.account import forms


class IndentedInvalidFieldsMixin:
    error_css_class = 'input-field-container has-error'


class SignupForm(IndentedInvalidFieldsMixin, forms.SignupForm):
    terms_agreed = BooleanField(
        label=mark_safe(
            'Tick this box to accept the '
            '<a href="/terms_and_conditions" target="_blank">terms and '
            'conditions</a> of the exporting is GREAT service.'
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password2'].label = 'Confirm password:'


class LoginForm(IndentedInvalidFieldsMixin, forms.LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['remember'].label = 'Remember me:'


class UserForm(IndentedInvalidFieldsMixin, forms.UserForm):
    pass


class AddEmailForm(IndentedInvalidFieldsMixin, forms.AddEmailForm):
    pass


class ChangePasswordForm(IndentedInvalidFieldsMixin, forms.ChangePasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password2'].label = 'Confirm password:'


class SetPasswordForm(IndentedInvalidFieldsMixin, forms.SetPasswordForm):
    pass


class ResetPasswordForm(IndentedInvalidFieldsMixin, forms.ResetPasswordForm):
    NO_ACCOUNT = 'There is no account for this email address'

    def clean_email(self):
        try:
            return super().clean_email()
        except ValidationError:
            raise ValidationError(self.NO_ACCOUNT)


class ResetPasswordKeyForm(IndentedInvalidFieldsMixin,
                           forms.ResetPasswordKeyForm):
    pass
