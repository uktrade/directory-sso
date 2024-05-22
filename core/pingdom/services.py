from django.db import DatabaseError

from sso.user.models import User


class DatabaseHealthCheck:
    name = 'database'

    def check(self):
        try:
            User.objects.all().exists()
        except DatabaseError as de:
            return False, de
        else:
            return True, ''


health_check_services = (DatabaseHealthCheck,)
