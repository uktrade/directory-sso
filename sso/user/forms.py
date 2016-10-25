from allauth.account import forms


class IndentedInvalidFieldsMixin:
    error_css_class = 'input-field-container has-error'


class SignupForm(IndentedInvalidFieldsMixin, forms.SignupForm):
    pass


class LoginForm(IndentedInvalidFieldsMixin, forms.LoginForm):
    pass


class UserForm(IndentedInvalidFieldsMixin, forms.UserForm):
    pass


class AddEmailForm(IndentedInvalidFieldsMixin, forms.AddEmailForm):
    pass


class ChangePasswordForm(IndentedInvalidFieldsMixin, forms.ChangePasswordForm):
    pass


class SetPasswordForm(IndentedInvalidFieldsMixin, forms.SetPasswordForm):
    pass


class ResetPasswordForm(IndentedInvalidFieldsMixin, forms.ResetPasswordForm):
    pass


class ResetPasswordKeyForm(IndentedInvalidFieldsMixin,
                           forms.ResetPasswordKeyForm):
    pass
