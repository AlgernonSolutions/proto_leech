import base64
import json
import os
from datetime import datetime
from os import path
from unittest.mock import MagicMock, patch

import pytest
from algernon import ajson


@pytest.fixture
def integration_environment():
    os.environ['BUCKET_NAME'] = 'algernonsolutions-leech-prod'
    os.environ['API_KEY_SECRET_ARN'] = 'arn:aws:secretsmanager:us-east-1:309427751091:secret:algernon_night_rider_service_account-ZUDcYA'
    os.environ['API_TABLE_NAME'] = 'NightRider'
    os.environ['QUEUE_URL'] = 'some_url'
    os.environ['HASH_KEY_NAME'] = 'identifier_stem'
    os.environ['SORT_KEY_NAME'] = 'sid_value'
    os.environ['EVENT_BUS_NAME'] = 'leech_bus'
    os.environ['app_id'] = 'botzu41'
    os.environ['env_id'] = 'ilq0e3i'
    os.environ['config_id'] = 'mvndveg'
    os.environ['aws_profile'] = 'NightRiderTest'


@pytest.fixture
def test_config():
    pass


@pytest.fixture(autouse=True)
def silence_x_ray():
    x_ray_patch_all = 'algernon.aws.lambda_logging.patch_all'
    patch(x_ray_patch_all).start()
    yield
    patch.stopall()


@pytest.fixture
def stored_event_generator():
    return _read_test_event


@pytest.fixture
def kinesis_event_generator():
    def generate_kinesis_event(event_name):
        event = _read_test_event(event_name)
        return {
            'Records': [
                {
                    'kinesis': {
                        'data': base64.b64encode(json.dumps(event).encode())
                    }
                }
            ]
        }
    return generate_kinesis_event


@pytest.fixture
def sqs_event_generator():
    def _generate_sqs_event(event_name):
        stored_event = _read_test_event(event_name)
        return {"Records": [{"body": ajson.dumps(stored_event)}]}
    return _generate_sqs_event


@pytest.fixture
def mock_response_generator():
    return _read_mock_response


@pytest.fixture(params=['PSI', 'ICFS'])
def id_source(request):
    return request.param


@pytest.fixture
def mock_id_source():
    return 'Algernon'


@pytest.fixture
def mock_context():
    context = MagicMock(name='context')
    context.__reduce__ = cheap_mock
    context.function_name = 'test_function'
    context.invoked_function_arn = 'test_function_arn'
    context.aws_request_id = '12344_request_id'
    context.get_remaining_time_in_millis.side_effect = [1000001, 500001, 250000, 0]
    return context


def cheap_mock(*args):
    from unittest.mock import Mock
    return Mock, ()


def _read_test_event(event_name):
    user_home = path.expanduser('~')
    with open(path.join(str(user_home),'.leech', '.algernon', 'proto_leech', f'{event_name}.json')) as json_file:
        event = json.load(json_file)
        return event


def _read_mock_response(event_name):
    with open(path.join('mock_responses', f'{event_name}.json')) as json_file:
        event = json.load(json_file)
        for entry, value in event.items():
            if 'Date' in entry:
                event[entry] = datetime.fromisoformat(value)
        return event
