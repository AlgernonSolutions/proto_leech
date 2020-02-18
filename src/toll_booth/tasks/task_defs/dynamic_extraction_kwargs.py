import os
from datetime import timedelta

import boto3
from algernon import build_alg_now


# noinspection PyUnusedLocal
def datetime_now(**kwargs):
    return build_alg_now()


def datetime_past(**kwargs):
    now = build_alg_now()
    delta_kwargs = {}
    years_set = False
    if 'years_ago' in kwargs:
        delta_kwargs['days'] = (int(kwargs['years_ago']) * 365)
        years_set = True
    if 'days_ago' in kwargs:
        if years_set:
            raise RuntimeError(f'cannot specify both years_ago and days_ago in the same dynamic_kwargs')
        delta_kwargs['days'] = int(kwargs['days_ago'])
    if 'hours_ago' in kwargs:
        delta_kwargs['hours'] = int(kwargs['hours_ago'])
    return now - timedelta(**delta_kwargs)


def environment_variable(**kwargs):
    variable_name = kwargs['variable_name']
    return os.environ[variable_name]


def _get_parameter(parameter_name: str):
    client = boto3.Session().client('ssm')
    response = client.get_parameter(
        Name=parameter_name
    )
    parameter_data = response['Parameter']
    return parameter_data['Value']


def id_source_specific_stored_parameter(**kwargs):
    common_parameters = kwargs['common_parameters']
    id_source = common_parameters.id_source
    parameter_name = f'{kwargs["parameter_name"]}.{id_source}'
    return _get_parameter(parameter_name)


def stored_parameter(**kwargs):
    parameter_name = kwargs['parameter_name']
    return _get_parameter(parameter_name)
