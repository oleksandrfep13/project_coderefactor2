import pytest
from datetime import datetime, timedelta
import uuid
from src.infrastructure.repositories import InMemoryMoodRepository
from src.domain.models import HealthEntry, EntryType


# --- Фікстури ---
@pytest.fixture
def repo():
    """Створює чистий екземпляр In-Memory репозиторію для кожного тесту."""
    return InMemoryMoodRepository()


def create_entry(id_str=None, value=5.0):
    """Допоміжна функція для генерації записів."""
    return HealthEntry(
        id=id_str or str(uuid.uuid4()),
        timestamp=datetime.now(),
        entry_type=EntryType.MOOD,
        value=float(value),
        note="In-memory test"
    )


# --- Тести ---

def test_repo_is_initially_empty(repo):
    """Новий репозиторій має бути порожнім."""
    assert repo.get_all() == []


def test_add_single_entry(repo):
    """Додавання одного запису та його отримання."""
    entry = create_entry(value=4.0)
    repo.add(entry)

    results = repo.get_all()
    assert len(results) == 1
    assert results[0].id == entry.id
    assert results[0].value == 4.0


def test_add_multiple_entries(repo):
    """Додавання кількох унікальних записів."""
    repo.add(create_entry())
    repo.add(create_entry())
    repo.add(create_entry())

    assert len(repo.get_all()) == 3


def test_add_overwrites_existing_id(repo):
    """
    Критичний тест: Оскільки дані зберігаються у словнику (Dict[str, HealthEntry]),
    додавання запису з існуючим ID має оновити старий запис, а не дублювати його.
    """
    shared_id = str(uuid.uuid4())
    entry_initial = create_entry(id_str=shared_id, value=2.0)
    repo.add(entry_initial)

    # Створюємо новий запис із тим САМИМ ID, але іншими даними
    entry_updated = HealthEntry(
        id=shared_id,
        timestamp=datetime.now(),
        entry_type=EntryType.MOOD,
        value=5.0,
        note="Updated Note"
    )
    repo.add(entry_updated)

    results = repo.get_all()
    assert len(results) == 1  # Словник не виріс
    assert results[0].value == 5.0
    assert results[0].note == "Updated Note"


def test_get_by_id_success(repo):
    """Успішний пошук запису за його ID."""
    entry = create_entry()
    repo.add(entry)

    found = repo.get_by_id(entry.id)
    assert found is not None
    assert found.id == entry.id


def test_get_by_id_not_found(repo):
    """Пошук неіснуючого ID має повертати None (завдяки використанню .get())."""
    repo.add(create_entry())
    assert repo.get_by_id("fake-uuid-123") is None


def test_repositories_are_isolated():
    """
    Перевірка відсутності 'витоку стану' на рівні класу.
    Два різні екземпляри In-Memory репозиторію повинні мати незалежні словники.
    """
    repo1 = InMemoryMoodRepository()
    repo2 = InMemoryMoodRepository()

    repo1.add(create_entry())

    assert len(repo1.get_all()) == 1
    assert len(repo2.get_all()) == 0



def test_get_by_date_filtering(repo):
    """Перевірка фільтрації за датою."""
    today = datetime.now()
    e1 = HealthEntry(str(uuid.uuid4()), today, EntryType.MOOD, 1.0, "")
    e2 = HealthEntry(str(uuid.uuid4()), today - timedelta(days=5), EntryType.MOOD, 2.0, "")
    repo.add(e1)
    repo.add(e2)

    assert len(repo.get_by_date(today)) == 1
    assert repo.get_by_date(today)[0].value == 1.0


def test_get_all_returns_copy(repo):
    """
    Важливо для in-memory: метод get_all() має повертати копію списку,
    щоб зовнішня зміна списку не ламала внутрішній стан репозиторію.
    """
    repo.add(create_entry())
    all_entries = repo.get_all()
    all_entries.clear()  # Намагаємося очистити отриманий список

    assert len(repo.get_all()) == 1  # Внутрішній стан не має змінитися


def test_add_multiple_types(repo):
    """Додавання записів різних типів (MOOD та HEALTH)."""
    e1 = HealthEntry(str(uuid.uuid4()), datetime.now(), EntryType.MOOD, 5.0, "")
    e2 = HealthEntry(str(uuid.uuid4()), datetime.now(), EntryType.HEALTH, 3.0, "")
    repo.add(e1)
    repo.add(e2)
    assert len(repo.get_all()) == 2


def test_large_volume_data(repo):
    """Перевірка продуктивності на 1000 записах."""
    for i in range(1000):
        repo.add(create_entry(id_str=str(i), value=float(i)))

    assert len(repo.get_all()) == 1000
    assert repo.get_by_id("500").value == 500.0

