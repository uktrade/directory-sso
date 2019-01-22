from allauth.account import forms
from directory_components.fields import DirectoryComponentsFieldMixin


class PasswordField(DirectoryComponentsFieldMixin, forms.PasswordField):
    pass
