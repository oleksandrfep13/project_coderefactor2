import pytest
from datetime import datetime
from src.application.services import HealthService
from src.application.analytics import AverageMoodStrategy, RecentTrendStrategy
from src.infrastructure.repositories import InMemoryMoodRepository
from src.domain.models import HealthEntry, EntryType


@pytest.fixture
def service():
    repo = InMemoryMoodRepository()
    # MoodService перейменовано на HealthService
    return HealthService(repo, AverageMoodStrategy())


# Тестуємо поведінку при порожньому репозиторії
def test_statistics_with_empty_repo(service):
    # Тепер ми вказуємо тип запису (MOOD)
    assert service.get_statistics(EntryType.MOOD) == 0.0


# Тестуємо TrendStrategy на порожньому репозиторії
def test_trend_strategy_empty():
    repo = InMemoryMoodRepository()
    service = HealthService(repo, RecentTrendStrategy())
    assert service.get_statistics(EntryType.MOOD) == 0.0


# Тестуємо TrendStrategy з малою кількістю записів
def test_trend_strategy_single_record():
    repo = InMemoryMoodRepository()
    strategy = RecentTrendStrategy()

    # Створюємо HealthEntry замість старого MoodRecord
    record = HealthEntry(
        id="1",
        timestamp=datetime.now(),
        entry_type=EntryType.MOOD,
        value=3.0,
        note="Test"
    )

    result = strategy.calculate([record])
    assert result == 0.0


# Тестуємо додавання запису (замість create_mood_record)
def test_add_entry(service):
    entry = service.add_entry(EntryType.MOOD, 5.0, "Чудовий день!")
    assert entry.value == 5.0
    assert len(service.repository.get_all()) == 1


# Тестуємо, що статистика рахується тільки для свого типу
def test_statistics_filtering(service):
    service.add_entry(EntryType.MOOD, 4.0, "Настрій")
    service.add_entry(EntryType.HEALTH, 2.0, "Пульс")

    # Середнє для MOOD має бути 4.0, а не (4+2)/2=3.0
    assert service.get_statistics(EntryType.MOOD) == 4.0