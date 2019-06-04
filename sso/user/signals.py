from core.helpers import createHash

import uuid


def create_uuid(sender, instance, *args, **kwargs):
    if instance.hashed_uuid is None:
        instance.hashed_uuid = createHash(uuid.uuid4())
