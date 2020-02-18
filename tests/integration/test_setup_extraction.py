import pytest


@pytest.mark.setup_i
@pytest.mark.usefixtures('integration_environment')
class TestSetupExtraction:
    def test_setup_extraction(self, stored_event_generator):
        from toll_booth.tasks.task_defs import setup_extraction

        event = stored_event_generator('setup_extraction')
        response = setup_extraction(**event['payload'])
        assert response
