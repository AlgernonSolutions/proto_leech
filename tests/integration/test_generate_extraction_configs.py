import pytest


@pytest.mark.configs_i
@pytest.mark.usefixtures('integration_environment')
class TestGenerateExtractionConfigs:
    def test_generate_extraction_configs(self, stored_event_generator):
        from toll_booth.tasks.task_defs import generate_extraction_config

        event = stored_event_generator('generate_extraction_configs')
        response = generate_extraction_config(**event['payload'])
        assert response
