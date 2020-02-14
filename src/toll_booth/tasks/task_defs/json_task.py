import re
from typing import Any

import jsonpath_rw


def _resolve_json_path(json, json_path: str):
    target_pattern = re.compile(r'(?P<child>\.(?:.(?!\.))+$)')
    child_value = target_pattern.search(json_path).group('child')
    parent_path = json_path.replace(child_value, '')
    child_value = child_value.replace('.', '')
    path = jsonpath_rw.parse(parent_path).find(json)[0]
    return path, child_value


def insert_json(json, json_path: str, insert_value: Any):
    if json_path == '$':
        return insert_value
    path, child_value = _resolve_json_path(json, json_path)
    path.value[child_value] = insert_value
    return json


def delete_json(json, json_path: str):
    path, child_value = _resolve_json_path(json, json_path)
    del(path.value[child_value])
    return json
