from django.core.management.commands.migrate import Command as MigrateCommand
from django.db import transaction
import csv
import ast

from sso.user.models import UserData, User


def inject_data(user, user_data_name, items):
    data_object = UserData.objects.filter(user=user, name=user_data_name).first()
    holding_data = []
    if data_object is None:
        data_object = UserData(user=user, name=user_data_name)

    if not data_object.data:
        holding_data = items
    else:
        if not any(data in items for data in data_object.data):
            holding_data = items + data_object.data

    data_object.data = holding_data
    data_object.save()


@transaction.atomic
def read_csv_and_save_basket(path):

    with open(path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            sso_id = (row["sso_id"],)
            export_countries = ast.literal_eval(row["export_countries"])
            export_commodity_codes = ast.literal_eval(row["export_commodity_codes"])

            # Check if user exist first.
            user = User.objects.filter(pk=sso_id[0]).first()
            if user is None:
                continue

            inject_data(user, "UserMarkets", export_countries)
            inject_data(user, "UserProducts", export_commodity_codes)


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
