import uuid

from core.helpers import createHash
from sso.user.models import UserProfile


def create_uuid(sender, instance, *args, **kwargs):
    if not instance.hashed_uuid:
        instance.hashed_uuid = createHash(uuid.uuid4())


def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        print("Profile created!")
