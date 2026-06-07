import uuid
from datetime import datetime
from typing import List
from src.domain.interfaces import IMoodRepository
from src.domain.models import HealthEntry, EntryType
from src.application.analytics import IAnalyticsStrategy

class HealthService:
    def __init__(self, repository: IMoodRepository, strategy: IAnalyticsStrategy):
        self.repository = repository
        self.strategy = strategy

    def add_entry(self, entry_type: EntryType, value: float, note: str, metadata: dict = None) -> HealthEntry:
        """Створює універсальний запис (настрій або показник здоров'я)"""
        entry = HealthEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            entry_type=entry_type,
            value=value,
            note=note,
            metadata=metadata or {}
        )
        self.repository.add(entry)
        return entry

    def get_statistics(self, entry_type: EntryType) -> float:
        """Розраховує статистику для конкретного типу записів"""
        all_entries = self.repository.get_all()
        # Фільтруємо записи перед тим, як віддати їх стратегії
        filtered_entries = [e for e in all_entries if e.entry_type == entry_type]
        return self.strategy.calculate(filtered_entries)

    def get_all_entries(self) -> List[HealthEntry]:
        return self.repository.get_all()