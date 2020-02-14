import logging
import traceback
from concurrent.futures.thread import ThreadPoolExecutor

import rapidjson
from algernon.aws import lambda_logged

from toll_booth.obj.troubles import ClientException
from toll_booth.tasks.task_handler import handle_queued_call, handle_direct_invocation, handle_proxy_call


@lambda_logged
def serve_api_call(event, context):
    logging.info(f'started serving a call to the api: {event}/{context}')
    try:
        results = handle_proxy_call(event)
        logging.info(f'completed a proxy_handler call [{event}]: {results}')
        return {'statusCode': 200, 'body': rapidjson.dumps(results)}
    except ClientException as e:
        exception_response = {
            'error_message': e.__class__.__name__,
            'error_details': e.message
        }
        logging.info(f'client error occurred during proxy_handler call [{event}]: {exception_response}')
        return {'statusCode': 400,  'body': rapidjson.dumps(exception_response)}
    except Exception as e:
        traceback.print_exc()
        exception_response = {
            'error_message': e.__class__.__name__,
            'error_details': e.args
        }
        logging.error(f'server error occurred during proxy_handler call [{event}]: {exception_response}')
        return {'statusCode': 500, 'body': rapidjson.dumps(exception_response)}


@lambda_logged
def work_queue(event, context):
    logging.info(f'received a call to start a work_queue task: {event}/{context}')
    promises = []
    with ThreadPoolExecutor() as executor:
        for record in event['Records']:
            message_body = rapidjson.loads(record['body'])
            if 'Message' in message_body:
                message_body = rapidjson.loads(message_body['Message'])
            promise = executor.submit(handle_queued_call, message_body)
            promises.append(promise)
        for promise in promises:
            promise.result()
    logging.info(f'completed a call to start a work_queue task: {event}')


@lambda_logged
def direct_invoke(event, context):
    logging.info(f'started a direct invocation: {event}/{context}')
    results = handle_direct_invocation(event)
    logging.info(f'completed a direct invocation [{event}]: {results}')
    return results
