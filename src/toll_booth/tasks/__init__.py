from __future__ import annotations

import os
from typing import NamedTuple

Config = 0


def _build_config() -> ConfigClass:
    config = ConfigClass(
        bucket_name=os.environ['BUCKET_NAME'],
        table_name=os.environ['API_TABLE_NAME'],
        queue_url=os.environ['QUEUE_URL'],
        hash_key_name=os.environ['HASH_KEY_NAME'],
        sort_key_name=os.environ['SORT_KEY_NAME']
    )
    return config


class ConfigClass(NamedTuple):
    bucket_name: str
    table_name: str
    hash_key_name: str
    sort_key_name: str
    queue_url: str


if Config is 0:
    Config = _build_config()
