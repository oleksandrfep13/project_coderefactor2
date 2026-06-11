import pytest
import os
import json
from datetime import datetime, timedelta
import uuid
from src.infrastructure.file_repositories import FileMoodRepository
from src.domain.models import HealthEntry, EntryType


@pytest.fixture
def repo_path(tmp_path):
    return str(tmp_path / "test_data.json")


@pytest.fixture
def repo(repo_path):
    return FileMoodRepository(repo_path)


def create_entry(entry_type, value, days_offset=0):
    dt = datetime.now() + timedelta(days=days_offset)
    return HealthEntry(
        id=str(uuid.uuid4()),
        timestamp=dt,
        entry_type=entry_type,
        value=float(value),
        note="Test Note"
    )


def test_get_all_empty_file(repo):
    assert repo.get_all() == []


def test_file_repository_add_and_get(repo):
    entry = create_entry(EntryType.MOOD, 5.0)
    repo.add(entry)
    results = repo.get_all()
    assert len(results) == 1
    assert results[0].id == entry.id
    assert results[0].value == 5.0


def test_add_creates_file(repo, repo_path):
    assert not os.path.exists(repo_path)
    repo.add(create_entry(EntryType.MOOD, 3.0))
    assert os.path.exists(repo_path)



def test_add_updates_existing_entry_same_date(repo):
    entry1 = create_entry(EntryType.MOOD, 3.0)
    repo.add(entry1)
    entry2 = HealthEntry(str(uuid.uuid4()), entry1.timestamp, EntryType.MOOD, 5.0, "Updated")
    repo.add(entry2)
    results = repo.get_all()
    assert len(results) == 1
    assert results[0].value == 5.0


def test_add_keeps_different_types_same_date(repo):
    entry_mood = create_entry(EntryType.MOOD, 4.0)
    entry_health = HealthEntry(str(uuid.uuid4()), entry_mood.timestamp, EntryType.HEALTH, 2.0, "Sick")
    repo.add(entry_mood)
    repo.add(entry_health)
    results = repo.get_all()
    assert len(results) == 2


def test_update_preserves_other_records(repo):
    yesterday = create_entry(EntryType.MOOD, 4.0, days_offset=-1)
    today_initial = create_entry(EntryType.MOOD, 2.0)
    repo.add(yesterday)
    repo.add(today_initial)

    today_updated = HealthEntry(str(uuid.uuid4()), today_initial.timestamp, EntryType.MOOD, 5.0, "")
    repo.add(today_updated)

    results = repo.get_all()
    assert len(results) == 2
    assert any(r.value == 4.0 for r in results)
    assert any(r.value == 5.0 for r in results)


def test_add_multiple_updates_sequentially(repo):
    base_time = datetime.now()
    for i in range(1, 6):
        repo.add(HealthEntry(str(uuid.uuid4()), base_time, EntryType.MOOD, float(i), ""))

    results = repo.get_all()
    assert len(results) == 1
    assert results[0].value == 5.0


def test_get_by_id(repo):
    entry = create_entry(EntryType.MOOD, 4.0)
    repo.add(entry)
    assert repo.get_by_id(entry.id).value == 4.0


def test_get_by_id_not_found(repo):
    repo.add(create_entry(EntryType.MOOD, 4.0))
    assert repo.get_by_id("non-existent-id") is None


def test_get_by_id_empty_repo(repo):
    assert repo.get_by_id("123") is None


def test_get_by_date(repo):
    today_entry = create_entry(EntryType.MOOD, 5.0)
    yesterday_entry = create_entry(EntryType.MOOD, 2.0, days_offset=-1)
    repo.add(today_entry)
    repo.add(yesterday_entry)

    today_results = repo.get_by_date(today_entry.timestamp)
    assert len(today_results) == 1
    assert today_results[0].value == 5.0


def test_get_by_date_no_matches(repo):
    repo.add(create_entry(EntryType.MOOD, 5.0))
    future_date = datetime.now() + timedelta(days=10)
    assert repo.get_by_date(future_date) == []



def test_persistence_between_instances(repo_path):
    repo1 = FileMoodRepository(repo_path)
    repo1.add(create_entry(EntryType.MOOD, 5.0))

    repo2 = FileMoodRepository(repo_path)
    assert len(repo2.get_all()) == 1


def test_exact_timestamp_preservation(repo):
    entry = create_entry(EntryType.MOOD, 3.0)
    repo.add(entry)
    loaded_entry = repo.get_all()[0]
    assert entry.timestamp == loaded_entry.timestamp


def test_malformed_json_raises_error(repo, repo_path):
    with open(repo_path, 'w') as f:
        f.write("{ invalid json [")

    with pytest.raises(json.JSONDecodeError):
        repo.get_all()


def test_get_all_with_empty_json_array(repo, repo_path):
    with open(repo_path, 'w') as f:
        f.write("[]")
    assert repo.get_all() == []


def test_add_same_entry_twice_is_idempotent(repo):
    entry = create_entry(EntryType.MOOD, 5.0)
    repo.add(entry)
    repo.add(entry)
    assert len(repo.get_all()) == 1


def test_add_many_entries_different_dates(repo):
    for i in range(30):
        repo.add(create_entry(EntryType.MOOD, 3.0, days_offset=i))
    assert len(repo.get_all()) == 30


def test_delete_entry(repo):
    entry = create_entry(EntryType.MOOD, 5.0)
    repo.add(entry)
    if hasattr(repo, 'delete'):
        repo.delete(entry.id)
        assert repo.get_by_id(entry.id) is None
        assert len(repo.get_all()) == 0


def test_file_permissions_error(repo_path):
    with open(repo_path, 'w') as f:
        f.write("[]")
    os.chmod(repo_path, 0o444)

    repo = FileMoodRepository(repo_path)
    with pytest.raises(Exception):
        repo.add(create_entry(EntryType.MOOD, 5.0))


def test_json_structure_preservation(repo, repo_path):
    repo.add(create_entry(EntryType.MOOD, 5.0))
    with open(repo_path, 'r') as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert "id" in data[0]
    assert "timestamp" in data[0]


def test_add_entry_with_empty_note(repo):
    entry = HealthEntry(str(uuid.uuid4()), datetime.now(), EntryType.MOOD, 1.0, "")
    repo.add(entry)
    assert repo.get_all()[0].note == ""


def test_get_all_sorting(repo):
    e1 = create_entry(EntryType.MOOD, 1.0, days_offset=-2)
    e2 = create_entry(EntryType.MOOD, 2.0, days_offset=-1)
    repo.add(e1)
    repo.add(e2)
    results = repo.get_all()
    assert results[0].timestamp < results[1].timestamp