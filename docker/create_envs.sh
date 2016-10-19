#!/bin/bash -xe

python ./docker/env_writer.py \
    ./docker/env.json \
    ./docker/env-postgres.json \
    ./docker/env.test.json \
    ./docker/env-postgres.test.json
