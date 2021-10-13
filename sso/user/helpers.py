import csv, ast
from sso.user.models import UserData, User
from django.core.exceptions import ObjectDoesNotExist


def read_csv_and_save_basket(path):
    with open(path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            sso_id = (row["sso_id"],)
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