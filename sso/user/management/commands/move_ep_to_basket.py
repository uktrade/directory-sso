import ast
import csv

from django.core.management.commands.migrate import Command as MigrateCommand
from django.db import transaction

from sso.user.models import User, UserData


def inject_data(user, user_data_name, items):
    data_object = UserData.objects.filter(user=user, name=user_data_name).first()
    data_object = data_object or UserData(user=user, name=user_data_name)

    if not data_object.data:
        data_object.data = items
    else:
        for item in items:
            if item not in data_object.data:
                data_object.data.append(item)

    data_object.save()


@transaction.atomic
def read_csv_and_save_basket(path, **kwargs):

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

            if kwargs.get('self'):
                self = kwargs.get('self')
                self.stdout.write(
                    self.style.NOTICE(
                        f"sso_id: {sso_id} with market: {export_countries} and product: {export_commodity_codes}."
                    )
                )
                self.stdout.write(self.style.NOTICE("---"))


class Command(MigrateCommand):
    """
    Move market and product from CSV to new basket.
    """

    def add_arguments(self, parser):
        parser.add_argument('path_to_file', type=str, help="Input path to CSV file.")

    def handle(self, *args, **options):
        my_file = options['path_to_file']

        self.stdout.write(self.style.WARNING("Starting migration process to basket."))
        try:
            read_csv_and_save_basket(my_file, self=self)
        except FileNotFoundError:
            self.stdout.write(self.style.WARNING(f'No file: {my_file} is found.'))
            raise FileNotFoundError

        self.stdout.write(self.style.SUCCESS("Migration to basket succesfully finished."))
