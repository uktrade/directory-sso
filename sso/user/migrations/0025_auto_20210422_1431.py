# Generated by Django 2.2.19 on 2021-04-22 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0024_add_predefined_choices'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='useranswer',
            options={'ordering': ('user', 'question__sort_order')},
        ),
        migrations.AlterField(
            model_name='question',
            name='predefined_choices',
            field=models.CharField(
                blank=True,
                choices=[
                    ('EXPERTISE_REGION_CHOICES', 'EXPERTISE_REGION_CHOICES'),
                    ('TURNOVER_CHOICES', 'TURNOVER_CHOICES'),
                    ('SECTORS', 'SECTORS'),
                ],
                max_length=128,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name='question',
            name='question_type',
            field=models.CharField(
                choices=[
                    ('RADIO', 'Radio'),
                    ('SELECT', 'Select'),
                    ('MULTI_SELECT', 'Multi select'),
                    ('TEXT', 'Text'),
                    ('COMPANY_LOOKUP', 'Company lookup'),
                ],
                max_length=20,
            ),
        ),
    ]