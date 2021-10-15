from django.core.management.commands.migrate import Command as MigrateCommand
from django.db import transaction
import csv
import ast

from sso.user.models import UserData, User


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

            for data_name in user_data_names:
                data_object = UserData.objects.filter(user=user, name=data_name).first()

                if data_object is None:
                    data_object = UserData(user=user, name=data_name)

                if data_name == user_data_names[0]:
                    data = export_countries
                else:
                    data = export_commodity_codes

                data_object.data = data
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
