import uuid
from typing import Mapping

import rapidjson

from algernon import ajson
from algernon.aws import StoredData

from toll_booth.obj.extraction import ExtractedData, ProcessedExtraction
from toll_booth.obj.extraction_config import ExtractionConfig
from toll_booth.tasks.task_defs import setup_tasks
from toll_booth.tasks.task_defs import config_tasks
from toll_booth.tasks.task_defs import extraction_tasks
from toll_booth.tasks.task_defs import processing_tasks
from toll_booth.tasks.task_defs import broadcast_tasks


def setup_extraction(
        id_source: str,
        source_name: str,
        object_type: str,
        extraction_type: str,
        extraction_params: Mapping = None
):
    setup_tasks.setup_extraction(
        id_source=id_source,
        source_name=source_name,
        object_type=object_type,
        extraction_type=extraction_type,
        extraction_params=extraction_params
    )


def generate_extraction_config(
        id_source: str,
        source_name: str,
        extraction_type: str,
        extraction_params: Mapping = None
):
    source_config, extraction_config = config_tasks.build_configs(
        id_source=id_source,
        source_name=source_name,
        extraction_type=extraction_type,
        extraction_params=extraction_params
    )
    results = {
        'source_config': source_config,
        'extraction_config': extraction_config
    }
    return rapidjson.loads(ajson.dumps(results))


def execute_extraction(
        extraction_config: ExtractionConfig
):
    extracted_data = extraction_tasks.execute_extraction(
        extraction_config=extraction_config
    )
    results = {'extracted_data': StoredData.from_object(uuid.uuid4().hex, extracted_data, True)}
    return rapidjson.loads(ajson.dumps(results))


def process_extraction(
        extraction_config: ExtractionConfig,
        extracted_data: ExtractedData
):
    processed_extraction = processing_tasks.process_extraction(
        extraction_config=extraction_config,
        extracted_data=extracted_data
    )
    results = {'processed_extraction': StoredData.from_object(uuid.uuid4().hex, processed_extraction, True)}
    return rapidjson.loads(ajson.dumps(results))


def broadcast_extracted_assets(
        processed_extraction: ProcessedExtraction
):
    broadcast_tasks.broadcast_extracted_assets(
        processed_extraction=processed_extraction
    )
