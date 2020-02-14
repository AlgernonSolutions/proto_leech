import logging

import rapidjson
from algernon import rebuild_event

from toll_booth.obj.troubles import UnknownInvocationException, UnknownProxyInvocationException
from toll_booth.tasks import task_defs


def handle_proxy_call(api_context):
    path = api_context['path']

    path = path.replace('/leech', '')
    path_pieces = path.split('/')
    root = path_pieces[1]
    fn = getattr(task_defs, root)
    if fn is None:
        raise UnknownProxyInvocationException(api_context['httpMethod'], path)
    payload = rapidjson.loads(api_context['body'])
    results = fn(**payload)
    return results


def handle_queued_call(queued_message):
    path = queued_message['path']
    path_pieces = path.split('/')
    root = path_pieces[1]
    fn = getattr(task_defs, root)
    if fn is None:
        raise UnknownInvocationException(root)
    payload = queued_message['payload']
    try:
        results = fn(**payload)
        return results
    except Exception as e:
        logging.error(f'terminal error while working a queued call: {e}')
        raise e


def handle_direct_invocation(event):
    path = event['path']
    path = path.replace('/soot', '')
    path_pieces = path.split('/')
    root = path_pieces[1]
    fn = getattr(task_defs, root)
    if fn is None:
        raise UnknownInvocationException(root)
    payload = event.get('payload', {})
    rebuilt_payload = rebuild_event(payload)
    results = fn(**rebuilt_payload)
    return results
