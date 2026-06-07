import pytest
from src.application.services import HealthService
from src.domain.models import EntryType, HealthEntry
from unittest.mock import MagicMock
from datetime import datetime

@pytest.fixture
def service():
    repo = MagicMock()
    strategy = MagicMock()
    return HealthService(repo, strategy)

@pytest.mark.parametrize("value, entry_type", [
    (1, EntryType.MOOD), (5, EntryType.MOOD), (2.5, EntryType.HEALTH),
    (0, EntryType.MOOD), (6, EntryType.HEALTH)
])
def test_add_entry(service, value, entry_type):
    service.add_entry(entry_type, value, "Test note")
    assert service.repository.add.called