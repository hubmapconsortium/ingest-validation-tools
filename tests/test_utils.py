import unittest
from unittest.mock import patch

from ingest_validation_tools.validation_utils import get_entity_api_data


class TestUtils(unittest.TestCase):

    @patch("ingest_validation_tools.validation_utils.requests.get")
    def test_get_entity_api_data_url(self, req_mock):
        test_entity_url = "https://entity.api.hubmapconsortium.org/entities"
        test_token = "test_token"
        test_id = "test_id"
        get_entity_api_data(test_entity_url, test_id, test_token)
        breakpoint()
        assert req_mock.called_once_with(
            test_entity_url + test_id + "?exclude=direct_ancestors.files",
            headers={"Authorization": f"Bearer {test_token}"},
        )
