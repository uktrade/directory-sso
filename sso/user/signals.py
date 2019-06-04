from core.helpers import createHash

import uuid


def create_uuid(sender, instance, *args, **kwargs):
    if not instance.hashed_uuid:
        instance.hashed_uuid = createHash(uuid.uuid4())
