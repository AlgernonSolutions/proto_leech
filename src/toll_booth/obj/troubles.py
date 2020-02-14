class EventPublishFailedException(Exception):
    """ raised when any Event messages cannot be published to the EventBridge.

    """

    def __init__(self, failed_entries):
        self._failed_entries = failed_entries


class MessagePublishFailedException(Exception):
    """ raised when any messages cannot be published to a given SQS queue.

    """
    def __init__(self, queue_url, failed_entries):
        self._queue_url = queue_url
        self._failed_entries = failed_entries


class ClientException(Exception):
    """ super class for exceptions based on client input

    """

    @property
    def message(self):
        raise NotImplementedError()


class UnknownProxyInvocationException(ClientException):
    def __init__(self, http_method: str, path: str):
        self._http_method = http_method
        self._path = path

    @property
    def message(self):
        return f'no idea how to process {self._path} using http method: {self._http_method}'


class UnknownInvocationException(ClientException):
    def __init__(self, task_name):
        self._task_name = task_name

    @property
    def message(self):
        return f'task {self._task_name} is not registered with the system'


class UnknownExtractionTypeException(ClientException):
    """ raised when an unregistered SnapshotType is invoked.

    """

    def __init__(self, snapshot_type: str):
        self._snapshot_type = snapshot_type

    @property
    def message(self):
        return f'snapshot_type {self._snapshot_type} is not registered with the system'


class UnknownExtractorException(ClientException):
    """ raised when an extraction is attempted with an unknown Extractor class.

    """

    def __init__(self, extractor_class: str):
        self._extractor_class = extractor_class

    @property
    def message(self):
        return f'extractor {self._extractor_class} is not registered with the system'


class UnknownProcessorException(ClientException):
    """ raised when an extraction is attempted with an unknown Processor class.

    """

    def __init__(self, processor_class: str):
        self._processor_class = processor_class

    @property
    def message(self):
        return f'processor {self._processor_class} is not registered with the system'
