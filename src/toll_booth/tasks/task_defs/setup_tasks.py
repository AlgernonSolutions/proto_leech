import uuid
from datetime import datetime
from typing import Tuple

import boto3
import rapidjson

from toll_booth.tasks import Config
from toll_booth.tasks.task_defs.tracing_tasks import mark_extraction_started, generate_identifier_stem

_client = None
if _client is None:
    _client = boto3.Session().client('stepfunctions')


def _start_machine(machine_arn, machine_payload) -> Tuple[str, datetime]:
    response = _client.start_execution(
        stateMachineArn=machine_arn,
        input=rapidjson.dumps(machine_payload)
    )
    execution_arn = response['executionArn']
    start_datetime = response['startDate']
    return execution_arn, start_datetime


def setup_extraction(
        id_source: str,
        source_name: str,
        object_type: str,
        extraction_type: str,
        extraction_params=None
):
    if extraction_params is None:
        extraction_params = {}
    machine_arn = Config.execution_machine_arn
    extraction_id = uuid.uuid4().hex
    identifier_stem = generate_identifier_stem(
        id_source=id_source,
        source_name=source_name,
        extraction_type=extraction_type,
        extraction_parameters=extraction_params
    )
    machine_payload = {
        'extraction_id': extraction_id,
        'identifier_stem': identifier_stem,
        'id_source': id_source,
        'source_name': source_name,
        'object_type': object_type,
        'extraction_type': extraction_type,
        'extraction_params': extraction_params
    }
    execution_arn, start_datetime = _start_machine(machine_arn, machine_payload)
    machine_payload.update({
        'execution_start_datetime': start_datetime.isoformat(),
        'execution_arn': execution_arn,
        'machine_arn': machine_arn
    })
    return mark_extraction_started(**machine_payload)
