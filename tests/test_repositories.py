import pytest
from src.infrastructure.file_repositories import FileMoodRepository
from src.domain.models import HealthEntry, EntryType
from datetime import datetime
import uuid


def test_file_repository_add_and_get(tmp_path):
    d = tmp_path / "test_data.json"
    repo = FileMoodRepository(str(d))

    entry = HealthEntry(str(uuid.uuid4()), datetime.now(), EntryType.MOOD, 5.0, "Happy")
    repo.add(entry)

    results = repo.get_all()
    assert len(results) == 1
    assert results[0].note == "Happy"