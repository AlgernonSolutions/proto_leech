from toll_booth.obj.extraction import ExtractedData
from toll_booth.obj.extraction_config import ExtractionConfig


class Extractor:
    @classmethod
    def generate(cls, extraction_config: ExtractionConfig):
        raise NotImplementedError()

    def perform_extraction(self, extraction_config: ExtractionConfig) -> ExtractedData:
        raise NotImplementedError()
