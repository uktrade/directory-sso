from core.helpers import createHash

import uuid


def create_uuid(sender, instance, *args, **kwargs):
    instance.hashed_uuid = createHash(uuid.uuid4())
