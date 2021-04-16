# Generated by Django 2.2.19 on 2021-04-15 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0023_auto_20210412_1614'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='predefined_choices',
            field=models.CharField(
                blank=True,
                choices=[
                    ('EXPERTISE_REGION_CHOICES', 'EXPERTISE_REGION_CHOICES'),
                    ('TURNOVER_CHOICES', 'TURNOVER_CHOICES'),
                ],
                max_length=128,
                null=True,
            ),
        ),
    ]