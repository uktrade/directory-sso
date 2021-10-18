from django.core.management.commands.migrate import Command as MigrateCommand
from django.db import transaction
import csv
import ast

from sso.user.models import UserData, User


def is_item_exist(list1, list2, dict_str_to_compare):
    try:
        if list1[0] and list2[0]:
            for item_a in list1:
                for item_b in list2:
                    if item_a[dict_str_to_compare] == item_b[dict_str_to_compare]:
                        return True
                    return False
    except IndexError:
        return False


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
            if user is None:
                continue

            # Loop via data names for UserMakers and UserProducts
            for data_name in user_data_names:
                data_object = UserData.objects.filter(user=user, name=data_name).first()

                # Create data if data does not exist
                if data_object is None:
                    data_object = UserData(user=user, name=data_name)

                # Default type is dictionary if empty converting to list so can append.
                if type(data_object.data) is dict:
                    if not data_object.data:
                        data_object.data = []

                data = data_object.data

                if data_name == user_data_names[0]:
                    if not is_item_exist(data_object.data, export_countries, "country_name"):
                        if export_countries:
                            data.append(export_countries[0])
                else:
                    if not is_item_exist(data_object.data, export_commodity_codes, "commodity_code"):
                        if export_commodity_codes:
                            data.append(export_commodity_codes[0])

                data_object.data = data
                print(data_object.data)
                data_object.save()


class Command(MigrateCommand):
    """
    Move market and product from CSV to new basket.
    """

    def add_arguments(self, parser):
        parser.add_argument('path_to_file', type=str, help="Input path to CSV file.")

    def handle(self, *args, **options):
        my_file = options['path_to_file']

        try:
            read_csv_and_save_basket(my_file)
        except FileNotFoundError:
            self.stdout.write(self.style.WARNING(f'No file: {my_file} is found.'))
            raise FileNotFoundError
