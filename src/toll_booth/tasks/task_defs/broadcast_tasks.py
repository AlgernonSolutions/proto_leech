import logging
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Sequence

import boto3
import rapidjson

from leech_tentacle.extraction import ProcessedExtraction, DataAsset
from toll_booth.obj.troubles import EventPublishFailedException


def _publish_batch_extracted_data(
        batch_extracted_data: Sequence[DataAsset]
):
    logging.debug(f'started publishing extracted_data events: {batch_extracted_data}')
    client = boto3.Session().client('events')
    response = client.put_events(
        Entries=[
            {
                'Source': 'spurious',
                'Resources': [f'{x.source_name.lower()}_{x.asset_type.lower()}'],
                'DetailType': 'publish_extracted_data',
                'Detail': rapidjson.dumps({
                    'id_source': x.id_source,
                    'source_name': x.source_name,
                    'capture_timestamp': x.capture_timestamp,
                    'asset_type': x.asset_type,
                    'asset_data': rapidjson.dumps(x.asset_data)
                })
            } for x in batch_extracted_data
        ]
    )
    if response['FailedEntryCount']:
        failed_entries = [x for x in response['Entries'] if x['ErrorCode'] or x['ErrorMessage']]
        raise EventPublishFailedException(failed_entries)
    logging.debug(f'completed publishing extracted_data events: {batch_extracted_data}')


def broadcast_extracted_assets(processed_extraction: ProcessedExtraction):
    promises = []
    batch = []
    with ThreadPoolExecutor() as executor:
        for entry in processed_extraction.processed_data:
            data_asset = DataAsset(
                id_source=processed_extraction.id_source,
                source_name=processed_extraction.source_name,
                capture_timestamp=processed_extraction.capture_timestamp,
                asset_type=processed_extraction.extracted_object_type,
                asset_data=entry
            )
            if len(batch) >= 10:
                promise = executor.submit(_publish_batch_extracted_data, batch)
                promises.append(promise)
                batch = []
            batch.append(data_asset)
        if batch:
            promise = executor.submit(_publish_batch_extracted_data, batch)
            promises.append(promise)
        for promise in promises:
            promise.result()
