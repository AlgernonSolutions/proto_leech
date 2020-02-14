import boto3
import rapidjson

from toll_booth.tasks import Config

queue = None
if queue is None:
    queue_url = Config.drive_hook_queue_url
    queue = boto3.resource('sqs').Queue(queue_url)


def publish_drive_hook(hook_message: str):
    queue.send_message(MessageBody=rapidjson.dumps(hook_message))
