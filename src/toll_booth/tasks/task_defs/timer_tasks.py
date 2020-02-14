from typing import List, Sequence

import boto3
import rapidjson

from toll_booth.obj.troubles import MessagePublishFailedException
from toll_booth.tasks import Config
from toll_booth.tasks.task_defs.tracing_tasks import get_table_item


queue = None
if queue is None:
    queue = boto3.Session().resource('sqs').Queue(Config.queue_url)


def _get_data_source_id_sources(source_name: str) -> List[str]:
    id_sources = []
    client = boto3.Session().client('dynamodb')
    paginator = client.get_paginator('scan')
    iterator = paginator.paginate(
        TableName=Config.table_name,
        FilterExpression='attribute_exists(#s.#sn) and #hk = :is',
        ExpressionAttributeNames={
            '#s': 'sources',
            '#sn': source_name,
            '#hk': Config.hash_key_name
        },
        ExpressionAttributeValues={
            ':is': {
                'S': '#id_source#'
            }
        }
    )
    for page in iterator:
        for entry in page.get('Items', []):
            id_sources.append(entry[Config.sort_key_name]['S'])
    return id_sources


def _publish_ordered_snapshots(ordered_snapshots: Sequence):
    response = queue.send_messages(
        Entries=[
            {
                'Id': str(x),
                'MessageBody': rapidjson.dumps({
                    'path': '/setup_extraction',
                    'payload': y
                })
            } for x, y in enumerate(ordered_snapshots)
        ]
    )
    failed_messages = response.get('Failed')
    if failed_messages:
        raise MessagePublishFailedException(Config.queue_url, failed_messages)


def hourly_timer(source_name: str):
    timer_profile = get_table_item(
        identifier_stem=f'#timed_extractions#{source_name}#',
        sid_value='hourly'
    )
    id_sources = _get_data_source_id_sources(
        source_name=source_name
    )
    timed_snapshots = timer_profile.get('snapshots', [])
    batch = []
    for snapshot in timed_snapshots:
        for id_source in id_sources:
            ordered_snapshot = {
                'extraction_type': snapshot['extraction_type'],
                'object_type': snapshot['object_type'],
                'extraction_parameters': snapshot.get('extraction_parameters', {}),
                'id_source': id_source,
                'source_name': source_name
            }
            if len(batch) >= 10:
                _publish_ordered_snapshots(batch)
                batch = []
            batch.append(ordered_snapshot)
        if batch:
            _publish_ordered_snapshots(batch)
