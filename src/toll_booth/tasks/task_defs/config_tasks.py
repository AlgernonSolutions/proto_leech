from copy import deepcopy
from typing import Mapping, Any, Sequence, NamedTuple

from toll_booth.obj.extraction_config import ExtractionConfig
from toll_booth.obj.extraction_template import TemplateParameters, RuntimeParameter, TemplatePrimitive, \
    ExtractionTemplate, ParameterSet
from toll_booth.obj.troubles import UnknownExtractionTypeException
from toll_booth.tasks.task_defs import dynamic_extraction_kwargs
from toll_booth.tasks.task_defs.json_task import insert_json
from toll_booth.tasks.task_defs.tracing_tasks import get_table_item


class CommonParameters(NamedTuple):
    id_source: str
    source_name: str
    extraction_type: str


def _get_config_template(extraction_type: str) -> ExtractionTemplate:
    return get_table_item('#extraction_config#', extraction_type)


def _resolve_dynamic_parameters(
        config_kwargs: TemplateParameters,
        common_parameters: CommonParameters
):
    resolved = {}
    for entry_name, entry in config_kwargs.items():
        if isinstance(entry, dict):
            if 'dynamic' in entry:
                if entry['dynamic'] is True:
                    dynamic_type = entry['dynamic_type']
                    dynamic_kwargs = entry.get('dynamic_kwargs', {})
                    dynamic_kwargs['common_parameters'] = common_parameters
                    resolving_fn = getattr(dynamic_extraction_kwargs, dynamic_type)
                    entry = resolving_fn(**dynamic_kwargs)
                    resolved[entry_name] = entry
                    continue
            entry = _resolve_dynamic_parameters(entry, common_parameters)
        resolved[entry_name] = entry
    return resolved


def _build_source_config(
        id_source: str,
        source_name: str
):
    item = get_table_item('#id_source#', id_source)
    if item is None:
        raise RuntimeError(f'id_source: {id_source} is not registered with the system')
    source = item['sources'].get(source_name)
    if source is None:
        raise RuntimeError(f'source: {source_name} is not configured for: {id_source}')
    source_config = source['config']
    config_values = {x: y for x, y in source_config.items()}
    return config_values


def _inject_runtime_parameters(
        runtime_parameters: Sequence[RuntimeParameter],
        resolved_parameters: Mapping[str, TemplatePrimitive],
        extraction_params: Mapping[str, TemplatePrimitive]
):
    parameters = deepcopy(resolved_parameters)
    for runtime_parameter in runtime_parameters:
        insert_path = runtime_parameter['insert_path']
        parameter_name = runtime_parameter['parameter_name']
        parameter_value = extraction_params[parameter_name]
        parameters = insert_json(parameters, insert_path, parameter_value)
    return parameters


def _build_template_parameter_set(
        parameter_set: ParameterSet,
        extraction_params,
        common_params: CommonParameters
):
    static_parameters = parameter_set.get('static_parameters', {})
    resolved_parameters = _resolve_dynamic_parameters(static_parameters, common_params)
    runtime_parameters = parameter_set.get('runtime_parameters', [])
    completed_parameters = _inject_runtime_parameters(runtime_parameters, resolved_parameters, extraction_params)
    return completed_parameters


def _build_extraction_config(
        id_source: str,
        source_name: str,
        extraction_type: str,
        extraction_params: Mapping[str, Any]
) -> ExtractionConfig:
    commons = CommonParameters(id_source, source_name, extraction_type)
    template = _get_config_template(extraction_type)
    if not template:
        raise UnknownExtractionTypeException(f'could not load an extraction template for {extraction_type}')
    extractor_template = template['extractor']
    processor_template = template['processor']
    return ExtractionConfig(
        id_source=id_source,
        source_name=source_name,
        extraction_type=extraction_type,
        extractor_class=extractor_template['extractor_class'],
        extractor_params=_build_template_parameter_set(extractor_template, extraction_params, commons),
        processor_class=processor_template['processor_class'],
        processor_params=_build_template_parameter_set(processor_template, extraction_params, commons),
        extracted_object_type=template['extracted_object_type'],
        extraction_params=_build_template_parameter_set(template['extraction'], extraction_params, commons)
    )


def build_configs(
        id_source: str,
        source_name: str,
        extraction_type: str,
        extraction_params: Mapping = None
):
    if extraction_params is None:
        extraction_params = {}
    source_config = _build_source_config(
        id_source=id_source,
        source_name=source_name
    )
    extraction_config = _build_extraction_config(
        id_source=id_source,
        source_name=source_name,
        extraction_type=extraction_type,
        extraction_params=extraction_params
    )
    return source_config, extraction_config
