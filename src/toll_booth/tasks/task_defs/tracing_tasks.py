import hashlib
from datetime import datetime
from decimal import Decimal
from typing import Mapping

import boto3
import rapidjson
from algernon import build_alg_now

from toll_booth.tasks import Config

tracer = None
if tracer is None:
    tracer = boto3.Session().resource('dynamodb').Table(Config.table_name)


def _generate_key(extraction_id: str, identifier_stem: str):
    return {
        Config.hash_key_name: identifier_stem,
        Config.sort_key_name: extraction_id
    }


def _sort_parameters(parameters):
    parameter_fields = {}
    if isinstance(parameters, list):
        parameters = {'parameters': parameters}
    for key_value, field_value in parameters.items():
        if isinstance(field_value, list):
            field_value = sorted(field_value)
        if isinstance(field_value, datetime):
            field_value = field_value.isoformat()
        if isinstance(field_value, float):
            field_value = Decimal(field_value)
        parameter_fields[key_value] = field_value
    return parameter_fields


def _generate_payload_hash(extraction_params: Mapping) -> str:
    parameter_values = _sort_parameters(extraction_params)
    parameters = rapidjson.dumps(parameter_values, sort_keys=True)
    hash_key = hashlib.md5(parameters.encode()).hexdigest()
    return hash_key


def generate_identifier_stem(
        id_source: str,
        source_name: str,
        extraction_type: str,
        extraction_parameters: Mapping
) -> str:
    parameter_values = _sort_parameters(extraction_parameters)
    parameters = rapidjson.dumps(parameter_values, sort_keys=True)
    hash_key = hashlib.md5(parameters.encode()).hexdigest()
    stem = f'#{id_source}#{source_name}#{extraction_type}#{hash_key}'
    return stem


def get_table_item(identifier_stem: str, sid_value: str):
    response = tracer.get_item(Key=_generate_key(sid_value, identifier_stem))
    return response['Item']


def mark_extraction_started(
        extraction_id: str,
        identifier_stem: str,
        extraction_type: str,
        object_type: str,
        id_source: str,
        source_name: str,
        machine_arn: str,
        execution_arn: str,
        execution_start_datetime: str,
        extraction_params=None
):
    if extraction_params is None:
        extraction_params = {}
    now = build_alg_now()
    item = {
        Config.hash_key_name: identifier_stem,
        Config.sort_key_name: extraction_id,
        'id_source': id_source,
        'source_name': source_name,
        'extraction_type': extraction_type,
        'start_timestamp': Decimal(now.timestamp()),
        'object_type': object_type,
        'extraction_parameters': extraction_params,
        'machine_arn': machine_arn,
        'machine_execution_arn': execution_arn,
        'execution_start_datetime': execution_start_datetime,
        'extraction_type_stem': f'#{id_source}#{source_name}#{extraction_type}#',
        'source_stem': f'#{id_source}#{source_name}#',
        'parameters_hash': _generate_payload_hash(extraction_params)
    }
    tracer.put_item(Item=item)
    return {'extraction_id': extraction_id, 'identifier_stem': identifier_stem}


def mark_extraction_success(identifier_stem: str, extraction_id: str):
    end_timestamp = build_alg_now()
    tracer.update_item(
        Key=_generate_key(extraction_id, identifier_stem),
        UpdateExpression='SET end_timestamp=:et',
        ExpressionAttributeValues={
            ':et': Decimal(str(end_timestamp.timestamp()))
        }
    )


def mark_extraction_fail(identifier_stem: str, extraction_id: str):
    fail_timestamp = build_alg_now()
    tracer.update_item(
        Key=_generate_key(extraction_id, identifier_stem),
        UpdateExpression='SET fail_timestamp=:ft',
        ExpressionAttributeValues={
            ':ft': Decimal(str(fail_timestamp.timestamp()))
        }
    )
