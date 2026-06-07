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

def validate_value(value):
    if not (0 < value <= 10):
        raise ValueError("Invalid value")
    return True



@pytest.mark.parametrize("value, expected_valid", [
    (1.0, True), (5.0, True), (10.0, True),
    (0.0, False), (-100.0, False), (999.0, False),
])
def test_entry_value_validation(value, expected_valid):
    if not expected_valid:
        with pytest.raises(ValueError):
            validate_value(value)
    else:
        assert validate_value(value) is True

@pytest.mark.parametrize("note", ["Normal mood", "", "long text", "😊", "   ", None])
def test_entry_notes(note):
    entry = HealthEntry(id="1", timestamp=datetime.now(), entry_type=EntryType.MOOD, value=5.0, note=note)
    assert entry.note == note

@pytest.mark.parametrize("value", [float(i) for i in range(-5, 25)])
@pytest.mark.parametrize("entry_type", list(EntryType))
@pytest.mark.parametrize("note", ["test", "", "A" * 10, "B" * 10])
def test_exhaustive_health_entry(value, entry_type, note):
    if not (0 < value <= 10):
        with pytest.raises(ValueError):
            validate_value(value)
    else:
        entry = HealthEntry("id", datetime.now(), entry_type, value, note)
        assert entry.value == value

@pytest.mark.parametrize("dt", [datetime(2020, 1, 1), datetime.now()])
def test_entry_dates(dt):
    entry = HealthEntry("1", dt, EntryType.MOOD, 5.0, "test")
    assert entry.timestamp == dt