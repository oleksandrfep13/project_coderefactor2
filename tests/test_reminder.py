import pytest
from unittest.mock import MagicMock
from datetime import datetime, timedelta
from src.domain.models import Reminder
from src.application.reminder import ReminderManager

@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.get_all.return_value = []
    return repo

@pytest.fixture
def manager(mock_repo):
    return ReminderManager(mock_repo)

def test_create_reminder(manager, mock_repo):
    rem = manager.create("Завдання 1", datetime.now())
    assert len(manager.get_all()) == 1
    mock_repo.save_all.assert_called()

def test_delete_existing(manager):
    rem = manager.create("Текст", datetime.now())
    assert manager.delete(rem.id) is True
    assert len(manager.get_all()) == 0

def test_delete_non_existent(manager):
    assert manager.delete("wrong-id") is False

def test_update_success(manager):
    rem = manager.create("Старий", datetime.now())
    manager.update(rem.id, text="Новий")
    assert manager.get_all()[0].text == "Новий"

def test_update_non_existent(manager):
    assert manager.update("fake-id", text="Нічого") is False

def test_get_all_sorts_by_date(manager):
    d1 = datetime(2026, 6, 1)
    d2 = datetime(2026, 6, 2)
    manager.create("Пізніше", d2)
    manager.create("Раніше", d1)
    results = manager.get_all()
    assert results[0].due_date == d1
    assert results[1].due_date == d2

def test_filter_completed(manager):
    r1 = manager.create("Активне", datetime.now())
    r2 = manager.create("Виконане", datetime.now())
    manager.update(r2.id, is_completed=True)
    assert len(manager.get_all(include_completed=False)) == 1

def test_update_only_one_field(manager):
    rem = manager.create("Текст", datetime.now())
    old_date = rem.due_date
    manager.update(rem.id, text="Зміна тексту")
    assert manager.get_all()[0].due_date == old_date

def test_get_all_empty(manager):
    assert manager.get_all() == []

def test_multiple_creates(manager):
    for i in range(5):
        manager.create(f"Task {i}", datetime.now())
    assert len(manager.get_all()) == 5

def test_update_completion_multiple_times(manager):
    rem = manager.create("Toggle", datetime.now())
    manager.update(rem.id, is_completed=True)
    manager.update(rem.id, is_completed=False)
    assert manager.get_all()[0].is_completed is False

def test_update_due_date(manager):
    rem = manager.create("Текст", datetime.now())
    new_date = datetime(2027, 1, 1)
    manager.update(rem.id, due_date=new_date)
    assert manager.get_all()[0].due_date == new_date

def test_persistence_on_update(manager, mock_repo):
    rem = manager.create("Текст", datetime.now())
    mock_repo.save_all.reset_mock()
    manager.update(rem.id, text="Новий")
    mock_repo.save_all.assert_called_once()

def test_integrity_after_delete_and_create(manager):
    r1 = manager.create("1", datetime.now())
    manager.delete(r1.id)
    r2 = manager.create("2", datetime.now())
    assert len(manager.get_all()) == 1
    assert manager.get_all()[0].text == "2"

def test_get_all_returns_sorted_list_copy(manager):
    manager.create("1", datetime.now())
    list1 = manager.get_all()
    list1.clear()
    assert len(manager.get_all()) == 1