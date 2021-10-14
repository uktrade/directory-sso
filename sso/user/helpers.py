import csv
import ast
from django.db import transaction

from sso.user.models import UserData, User
from django.core.exceptions import ObjectDoesNotExist


@transaction.atomic
def read_csv_and_save_basket(path):

    with open(path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        count = 0

        for row in reader:
            count += 1
            sso_id = (row["sso_id"],)
            export_countries = ast.literal_eval(row["export_countries"])
            export_commodity_codes = ast.literal_eval(row["export_commodity_codes"])

            user_data_names = ("UserMarkets", "UserProducts")

            # Check if user exist first.
            user = User.objects.filter(pk=sso_id[0]).first()
            if user == None:
                continue

            for data_name in user_data_names:
                data_object = UserData.objects.filter(user=user, name=data_name).first()

                if data_object == None:
                    data_object = UserData(user=user, name=data_name)

                if data_name == user_data_names[0]:
                    data = export_countries
                if data_name == user_data_names[1]:
                    data = export_commodity_codes

                data_object.data = data
                data_object.save()
