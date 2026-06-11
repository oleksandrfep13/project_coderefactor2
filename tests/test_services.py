import pytest
from unittest.mock import MagicMock
from datetime import datetime, timedelta
import uuid
from src.application.services import HealthService
from src.domain.models import HealthEntry, EntryType, Reminder


# --- Фікстури ---
@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def mock_strategy():
    strategy = MagicMock()
    strategy.calculate.return_value = 42.0
    return strategy


@pytest.fixture
def service(mock_repo, mock_strategy):
    return HealthService(mock_repo, mock_strategy)


def create_mock_entry(entry_type, value):
    return HealthEntry(str(uuid.uuid4()), datetime.now(), entry_type, float(value), "test")


# ==========================================
# Тести для методу: add_entry
# ==========================================

def test_add_entry_basic_creation(service, mock_repo):
    """1. Базове створення: перевірка правильного мапінгу полів."""
    result = service.add_entry(EntryType.MOOD, 5.0, "Great day")
    assert result.entry_type == EntryType.MOOD
    assert result.value == 5.0
    assert result.note == "Great day"


def test_add_entry_uuid_generation(service):
    """2. Перевірка, що сервіс генерує валідний UUID4 для нового запису."""
    result = service.add_entry(EntryType.HEALTH, 4.0, "Ok")
    # Якщо це не валідний UUID, наступний рядок викине помилку
    parsed_uuid = uuid.UUID(result.id, version=4)
    assert str(parsed_uuid) == result.id


def test_add_entry_timestamp_is_current(service):
    """3. Перевірка, що час створення встановлюється автоматично і є актуальним."""
    before_call = datetime.now()
    result = service.add_entry(EntryType.MOOD, 3.0, "Normal")
    after_call = datetime.now()
    assert before_call <= result.timestamp <= after_call


def test_add_entry_calls_repo(service, mock_repo):
    """4. Перевірка інтеграції: чи дійсно запис передається в репозиторій."""
    result = service.add_entry(EntryType.HEALTH, 2.0, "Bad")
    mock_repo.add.assert_called_once_with(result)


def test_add_entry_metadata_handling(service):
    """5. Перевірка обробки метаданих: передані та за замовчуванням."""
    res_with_meta = service.add_entry(EntryType.MOOD, 5.0, "", metadata={"city": "Lviv"})
    res_no_meta = service.add_entry(EntryType.MOOD, 5.0, "")

    assert res_with_meta.metadata == {"city": "Lviv"}
    assert res_no_meta.metadata == {}  # Має бути порожній словник, а не None



def test_set_strategy_initial_state(service, mock_strategy):
    assert service.strategy == mock_strategy


def test_set_strategy_replaces_instance(service):
    new_strategy = MagicMock()
    service.set_strategy(new_strategy)
    assert service.strategy == new_strategy


def test_set_strategy_old_is_not_called(service, mock_strategy, mock_repo):
    new_strategy = MagicMock()
    service.set_strategy(new_strategy)

    mock_repo.get_all.return_value = []
    service.get_analytics()

    new_strategy.calculate.assert_called_once()
    mock_strategy.calculate.assert_not_called()


def test_set_strategy_multiple_changes(service):
    strat1, strat2, strat3 = MagicMock(), MagicMock(), MagicMock()
    service.set_strategy(strat1)
    assert service.strategy == strat1
    service.set_strategy(strat2)
    service.set_strategy(strat3)
    assert service.strategy == strat3


def test_set_strategy_calculate_delegation(service):
    new_strategy = MagicMock()
    new_strategy.calculate.return_value = 100.0
    service.set_strategy(new_strategy)

    assert service.get_analytics() == 100.0


def test_get_analytics_no_filter_calls_strategy(service, mock_repo, mock_strategy):
    entries = [create_mock_entry(EntryType.MOOD, 1), create_mock_entry(EntryType.HEALTH, 2)]
    mock_repo.get_all.return_value = entries
    service.get_analytics()
    mock_strategy.calculate.assert_called_once_with(entries)


def test_get_analytics_filters_by_mood(service, mock_repo, mock_strategy):
    mood1 = create_mock_entry(EntryType.MOOD, 5.0)
    mood2 = create_mock_entry(EntryType.MOOD, 4.0)
    health1 = create_mock_entry(EntryType.HEALTH, 3.0)
    mock_repo.get_all.return_value = [mood1, health1, mood2]

    service.get_analytics(EntryType.MOOD)
    mock_strategy.calculate.assert_called_once_with([mood1, mood2])


def test_get_analytics_filters_by_health(service, mock_repo, mock_strategy):
    health1 = create_mock_entry(EntryType.HEALTH, 2.0)
    mood1 = create_mock_entry(EntryType.MOOD, 5.0)
    mock_repo.get_all.return_value = [health1, mood1]

    service.get_analytics(EntryType.HEALTH)
    mock_strategy.calculate.assert_called_once_with([health1])


def test_get_analytics_empty_repo(service, mock_repo, mock_strategy):
    mock_repo.get_all.return_value = []
    service.get_analytics(EntryType.MOOD)
    mock_strategy.calculate.assert_called_once_with([])


def test_get_analytics_returns_calculated_value(service, mock_repo, mock_strategy):
    mock_repo.get_all.return_value = []
    mock_strategy.calculate.return_value = 8.5
    assert service.get_analytics() == 8.5


def test_get_statistics_exact_filter(service, mock_repo, mock_strategy):
    target = create_mock_entry(EntryType.HEALTH, 4.0)
    noise = create_mock_entry(EntryType.MOOD, 5.0)
    mock_repo.get_all.return_value = [noise, target, noise]

    service.get_statistics(EntryType.HEALTH)
    mock_strategy.calculate.assert_called_once_with([target])


def test_get_statistics_no_matches(service, mock_repo, mock_strategy):
    mock_repo.get_all.return_value = [create_mock_entry(EntryType.HEALTH, 3.0)]
    service.get_statistics(EntryType.MOOD)
    mock_strategy.calculate.assert_called_once_with([])


def test_get_statistics_returns_result(service, mock_repo, mock_strategy):
    mock_strategy.calculate.return_value = 12.34
    assert service.get_statistics(EntryType.MOOD) == 12.34


def test_get_statistics_empty_repo(service, mock_repo, mock_strategy):
    mock_repo.get_all.return_value = []
    service.get_statistics(EntryType.HEALTH)
    mock_strategy.calculate.assert_called_once_with([])


def test_get_statistics_maintains_order(service, mock_repo, mock_strategy):
    e1 = create_mock_entry(EntryType.MOOD, 1.0)
    e2 = create_mock_entry(EntryType.MOOD, 2.0)
    mock_repo.get_all.return_value = [e1, create_mock_entry(EntryType.HEALTH, 5.0), e2]

    service.get_statistics(EntryType.MOOD)
    mock_strategy.calculate.assert_called_once_with([e1, e2])


def test_get_all_entries_delegation(service, mock_repo):
    service.get_all_entries()
    mock_repo.get_all.assert_called_once()


def test_get_all_entries_returns_list(service, mock_repo):
    expected = [create_mock_entry(EntryType.MOOD, 5.0)]
    mock_repo.get_all.return_value = expected
    assert service.get_all_entries() == expected


def test_get_all_entries_empty(service, mock_repo):
    mock_repo.get_all.return_value = []
    assert service.get_all_entries() == []


def test_get_all_entries_multiple_calls(service, mock_repo):
    mock_repo.get_all.return_value = []
    service.get_all_entries()
    service.get_all_entries()
    assert mock_repo.get_all.call_count == 2


def test_get_all_entries_passes_exceptions(service, mock_repo):
    mock_repo.get_all.side_effect = Exception("Database connection lost")
    with pytest.raises(Exception, match="Database connection lost"):
        service.get_all_entries()


def test_add_entry_rejects_past_date(service):
    yesterday = datetime.now() - timedelta(days=1)

    with pytest.raises(ValueError, match="Записи можна додавати та змінювати лише для поточного дня!"):
        service.add_entry(EntryType.MOOD, 3.0, "Вчорашній запис", timestamp=yesterday)


def test_add_entry_rejects_future_date(service):
    tomorrow = datetime.now() + timedelta(days=1)

    with pytest.raises(ValueError, match="Записи можна додавати та змінювати лише для поточного дня!"):
        service.add_entry(EntryType.HEALTH, 5.0, "Завтрашній запис", timestamp=tomorrow)




def test_analytics_with_filtered_data_stability(service, mock_repo, mock_strategy):
    e1 = create_mock_entry(EntryType.MOOD, 5.0)
    e2 = create_mock_entry(EntryType.HEALTH, 3.0)
    mock_repo.get_all.return_value = [e1, e2]

    service.get_analytics(EntryType.MOOD)

    mock_strategy.calculate.assert_called_once_with([e1])



def test_complex_analytics_chain(service, mock_repo, mock_strategy):
    mock_repo.get_all.return_value = [create_mock_entry(EntryType.MOOD, 4.0)]

    strat2 = MagicMock()
    strat2.calculate.return_value = 99.0
    service.set_strategy(strat2)

    result = service.get_analytics(EntryType.MOOD)
    assert result == 99.0
    strat2.calculate.assert_called()