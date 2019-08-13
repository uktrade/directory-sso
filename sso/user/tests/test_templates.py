import os

from directory_components.context_processors import urls_processor
import pytest

from django.conf import settings
from django.template.loader import render_to_string


template_names = []
for template_dir in settings.TEMPLATES[0]['DIRS']:
    for dir, dirnames, filenames in os.walk(template_dir):
        for filename in filenames:
            template = os.path.join(dir, filename).replace(template_dir, '')
            template_names.append(template.lstrip('/'))


@pytest.mark.parametrize('template_name', template_names)
def test_templates_render_successfully(template_name):
    context = {
        'user': None,
        **urls_processor(None),
    }
    render_to_string(template, context)
