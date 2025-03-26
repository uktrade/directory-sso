import argparse
import urllib.parse

from django.core.management import BaseCommand

from sso.user.models import User, UserData, UserProfile


class Command(BaseCommand):
    help = 'Obsfucate Personal Details'

    START_INDEX = 1
    END_INDEX = -1
    MASK_CHAR = '*'

    def mask_email_data(self, data):
        if not data:
            return data
        name = data.split('@')[0]
        address = data.split('@')[1]
        name = self.mask_string_data(name)
        address = self.mask_string_data(address)
        return f'{name}@{address}'

    def mask_string_data(self, data):
        if not data:
            return data
        ret = f'{data[:self.START_INDEX]}{self.MASK_CHAR * len(data[self.START_INDEX:self.END_INDEX])}{data[self.END_INDEX:]}'
        return ret

    def mask_json_data(self, data, fields):
        for field in fields:
            try:
                masked_field = self.mask_string_data(data[field])
                data[field] = masked_field
            except KeyError:
                pass
            else:
                data[field] = masked_field
        return data

    def mask_user(self, user, options):
        print(user.email)
        print(user.first_name)
        print(user.last_name)

        user.email = self.mask_email_data(user.email)
        user.first_name = self.mask_string_data(user.first_name)
        user.last_name = self.mask_string_data(user.last_name)
        user.password = self.mask_string_data(user.password)

        if options['dry_run'] is False:
            pass
            # user.save()
        print(user.email)
        print(user.first_name)
        print(user.last_name)
        print(user.password)

    def mask_user_profile(self, user_profile, options):
        print(user_profile.first_name)
        print(user_profile.last_name)
        print(user_profile.mobile_phone_number)

        user_profile.first_name = self.mask_string_data(user_profile.first_name)
        user_profile.last_name = self.mask_string_data(user_profile.last_name)
        user_profile.mobile_phone_number = self.mask_string_data(user_profile.mobile_phone_number)

        if options['dry_run'] is False:
            pass
            # user_profile.save()
        print(user_profile.first_name)
        print(user_profile.last_name)
        print(user_profile.mobile_phone_number)

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry_run',
            action=argparse.BooleanOptionalAction,
            default=False,
            help='Show summary output only, do not update data',
        )

    def handle(self, *args, **options):  # noqa: C901

        # Obsfucate User Data
        for user in User.objects.all():
            self.mask_user(user, options)

        # Obsfucate UserProfile  Data
        for user_profile in UserProfile.objects.all():
            self.mask_user_profile(user_profile, options)

        if options['dry_run'] is True:
            self.stdout.write(self.style.WARNING('Dry run -- no data updated.'))

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
