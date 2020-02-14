from toll_booth.obj.extraction import ExtractedData, ProcessedExtraction
from toll_booth.obj import processors
from toll_booth.obj.extraction_config import ExtractionConfig
from toll_booth.obj.processors import Processor
from toll_booth.obj.troubles import UnknownProcessorException


def _build_processor(
        extraction_config: ExtractionConfig
) -> Processor:
    processing_class = getattr(processors, extraction_config.processor_class)
    if processing_class is None:
        raise UnknownProcessorException(extraction_config.processor_class)
    processor = processing_class.generate(extraction_config)
    return processor


def process_extraction(
        extracted_data: ExtractedData,
        extraction_config: ExtractionConfig
) -> ProcessedExtraction:
    processor = _build_processor(extraction_config)
    processed_extraction = processor.process(extracted_data)
    return processed_extraction
