from django.db import migrations
from pathlib import Path
from sso.user.helpers import read_csv_and_save_basket

my_file = Path("ep_plan.csv")


def adds_items_to_basket_from_csv(apps, schema_editor):
    read_csv_and_save_basket(my_file)


class Migration(migrations.Migration):
    dependencies = [
        ('user', '0026_auto_20210429_1613'),
    ]

    if my_file.is_file():
        operations = [
            migrations.RunPython(adds_items_to_basket_from_csv, migrations.RunPython.noop),
        ]
