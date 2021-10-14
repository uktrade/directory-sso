from django.core.management.commands.migrate import Command as MigrateCommand
from sso.user import helpers


class Command(MigrateCommand):
    """
    Move market and product from CSV to new basket.
    """

    def add_arguments(self, parser):
        parser.add_argument('path_to_file', type=str, help="Input path to CSV file.")

    def handle(self, *args, **options):
        my_file = options['path_to_file']

        try:
            helpers.read_csv_and_save_basket(my_file)
        except FileNotFoundError:
            self.stdout.write(self.style.WARNING(f'No file: {my_file} is found.'))
