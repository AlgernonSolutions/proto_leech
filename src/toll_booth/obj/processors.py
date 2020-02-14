from __future__ import annotations

from toll_booth.obj.extraction import ExtractedData, ProcessedExtraction
from toll_booth.obj.extraction_config import ExtractionConfig


class Processor:
    @classmethod
    def generate(cls, extraction_config: ExtractionConfig) -> Processor:
        raise NotImplementedError()

    def process(self, extraction: ExtractedData) -> ProcessedExtraction:
        raise NotImplementedError()
