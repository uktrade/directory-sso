from django import forms

from sso.user import widgets


def test_checkbox_with_inline_label():

    class MyTestForm(forms.Form):
        checkbox = forms.BooleanField(
            widget=widgets.CheckboxWithInlineLabel(label='the label')
        )

    form = MyTestForm()

    expected_html = """
        <div class="form-field checkbox">
            <input id="id_checkbox" name="checkbox" type="checkbox" required />
            <label for="id_checkbox">the label</label>
        </div>
    """

    assert expected_html in str(form)
