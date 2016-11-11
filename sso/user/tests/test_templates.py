from django.conf import settings
from django.template.loader import render_to_string
import os


template_list = []
for template_dir in settings.TEMPLATES[0]['DIRS']:
    for dir, dirnames, filenames in os.walk(template_dir):
        for filename in filenames:
            template = os.path.join(dir, filename).replace(template_dir, '')
            template_list.append(template.lstrip('/'))


def test_templates_render_successfully():
    default_context = {'user': None}
    assert template_list
    for template in template_list:
        render_to_string(template, default_context)
