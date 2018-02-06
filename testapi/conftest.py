from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def mock_signature_checker():
    mock_path = 'sigauth.utils.RequestSignatureChecker.test_signature'
    patcher = patch(mock_path, return_value=True)
    patcher.start()
    yield
    patcher.stop()
