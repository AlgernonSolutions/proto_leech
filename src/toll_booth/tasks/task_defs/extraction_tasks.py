from toll_booth.obj.extraction import ExtractedData
from toll_booth.obj.extraction_config import ExtractionConfig
from toll_booth.obj import extractors
from toll_booth.obj.extractors import Extractor
from toll_booth.obj.troubles import UnknownExtractorException


def _build_extractor(extraction_config: ExtractionConfig) -> Extractor:
    extractor_class = getattr(extractors, extraction_config.extractor_class)
    if extractor_class is None:
        raise UnknownExtractorException(extraction_config.extractor_class)
    extractor = extractor_class.generate(extraction_config)
    return extractor


def execute_extraction(extraction_config: ExtractionConfig) -> ExtractedData:
    extractor = _build_extractor(extraction_config)
    return extractor.perform_extraction(extraction_config)
