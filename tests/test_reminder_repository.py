import pytest
import json
from datetime import datetime
from src.domain.models import Reminder
from src.infrastructure.reminder_repositories import FileReminderRepository


@pytest.fixture
def repo_path(tmp_path):
    return str(tmp_path / "reminders.json")


@pytest.fixture
def repo(repo_path):
    return FileReminderRepository(repo_path)


def test_load_empty_file(repo):
    assert repo.get_all() == []


def test_save_and_load(repo):
    reminders = [
        Reminder(id="1", text="Тест 1", due_date=datetime(2026, 6, 1), is_completed=False),
        Reminder(id="2", text="Тест 2", due_date=datetime(2026, 6, 2), is_completed=True)
    ]

    repo.save_all(reminders)
    loaded = repo.get_all()

    assert len(loaded) == 2
    assert loaded[0].text == "Тест 1"
    assert loaded[1].is_completed is True


def test_persistence_between_instances(repo_path):
    repo1 = FileReminderRepository(repo_path)
    reminders = [Reminder(id="1", text="Persistent", due_date=datetime.now(), is_completed=False)]
    repo1.save_all(reminders)

    repo2 = FileReminderRepository(repo_path)
    assert len(repo2.get_all()) == 1
    assert repo2.get_all()[0].text == "Persistent"


def test_file_format_is_json(repo, repo_path):
    repo.save_all([Reminder(id="1", text="Format", due_date=datetime.now(), is_completed=False)])

    with open(repo_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert data[0]["text"] == "Format"


def test_save_empty_list(repo):
    repo.save_all([])
    assert repo.get_all() == []


def test_encoding_support(repo, repo_path):
    text = "Нагадування: Привіт!"
    repo.save_all([Reminder(id="1", text=text, due_date=datetime.now(), is_completed=False)])

    loaded = repo.get_all()
    assert loaded[0].text == text