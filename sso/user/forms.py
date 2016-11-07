from django.forms import BooleanField, ValidationError
from django.utils.safestring import mark_safe

from allauth.account import forms
from allauth.utils import set_form_field_order


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
    field_order = [
        'email',
        'email2',
        'password1',
        'password2',
        'terms_agreed',
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password2'].label = 'Confirm password:'
        self.fields['email2'].label = 'Confirm email:'
        set_form_field_order(self, self.field_order)


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
