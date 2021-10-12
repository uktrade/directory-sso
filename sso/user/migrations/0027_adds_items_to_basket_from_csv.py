from django.core.exceptions import ObjectDoesNotExist
from django.db import migrations
from sso.user.models import UserData, User
import csv, ast
from pathlib import Path


def adds_items_to_basket_from_csv(apps, schema_editor):

    with open("ep_plan.csv", 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            sso_id = row["sso_id"],
            export_countries = ast.literal_eval(row["export_countries"])
            export_commodity_codes = ast.literal_eval(row["export_commodity_codes"])

            user_data_names = ["UserMarkets", "UserProducts"]
            
            # Check if users exist first.
            try:
                user = User.objects.get(pk=sso_id[0])
            except ObjectDoesNotExist:
                continue

            for data_name in user_data_names:
                try:
                    data_object = UserData.objects.get(user=user, name=data_name)
                except ObjectDoesNotExist:
                    data_object = UserData(user=user, name=data_name)

                if data_name == "UserMarkets":
                    data = export_countries
                if data_name == "UserProducts":
                    data = export_commodity_codes

                data_object.data = data
                data_object.save()


class Migration(migrations.Migration):
    my_file = Path("ep_plan.csv")

    dependencies = [
        ('user', '0026_auto_20210429_1613'),
    ]

    if my_file.is_file():
        operations = [
            migrations.RunPython(adds_items_to_basket_from_csv, migrations.RunPython.noop),
        ]
