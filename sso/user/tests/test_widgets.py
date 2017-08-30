import pytest

from django import forms

from sso.user import widgets


def minify_html(html):
    return html.replace('  ', '').replace('\n', '')


@pytest.mark.skip('The <input attributes are non deterministic order')
def test_checkbox_with_inline_label():

    class MyTestForm(forms.Form):
        checkbox = forms.BooleanField(
            widget=widgets.CheckboxWithInlineLabel(label='the label')
        )

    form = MyTestForm()

    expected_html = """
        <div class="form-field checkbox">
            <input type="checkbox" name="checkbox" required id="id_checkbox" />
            <label for="id_checkbox">the label</label>
        </div>
    """

    assert minify_html(expected_html) in minify_html(str(form))
