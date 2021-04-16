# Generated by Django 2.2.19 on 2021-04-09 08:01

import sort_order_field.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0021_auto_20210408_1013'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ('sort_order',)},
        ),
        migrations.RemoveField(
            model_name='question',
            name='order',
        ),
        migrations.AddField(
            model_name='question',
            name='sort_order',
            field=sort_order_field.fields.SortOrderField(db_index=True, default=0, verbose_name='Sort'),
        ),
    ]
