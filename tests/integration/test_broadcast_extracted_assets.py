import pytest


@pytest.mark.broadcast_i
@pytest.mark.usefixtures('integration_environment')
class TestBroadcastExtractedAssets:
    def test_broadcast_extracted_assets(self, stored_event_generator):
        from toll_booth.tasks.task_defs import broadcast_extracted_assets

        event = stored_event_generator('broadcast_extracted_assets')
        response = broadcast_extracted_assets(**event)
        assert response
