from unittest import mock

import pytest

from signature.utils import SignatureRejection


@pytest.fixture(autouse=True)
def mock_signature_rejection(monkeypatch):
    monkeypatch.setattr(
        SignatureRejection,
        'test_signature',
        mock.Mock(return_value=True)
    )
