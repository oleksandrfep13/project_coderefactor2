import uuid
from datetime import datetime
from typing import List
from src.domain.interfaces import IMoodRepository
from src.domain.models import HealthEntry, EntryType, Reminder
from src.application.analytics import IAnalyticsStrategy

class HealthService:
    def __init__(self, repository: IMoodRepository, strategy: IAnalyticsStrategy):
        self.repository = repository
        self.strategy = strategy

    def add_entry(self, entry_type: EntryType, value: float, note: str, timestamp: datetime = None,
                  metadata: dict = None) -> HealthEntry:
        target_date = timestamp or datetime.now()

        if target_date.date() != datetime.now().date():
            raise ValueError("Записи можна додавати та змінювати лише для поточного дня!")

        entry = HealthEntry(
            id=str(uuid.uuid4()),
            timestamp=target_date,
            entry_type=entry_type,
            value=value,
            note=note,
            metadata=metadata or {}
        )
        self.repository.add(entry)
        return entry

    def set_strategy(self, strategy: IAnalyticsStrategy):
        self.strategy = strategy

    def get_analytics(self, entry_type: EntryType = None) -> float:
        entries = self.repository.get_all()
        if entry_type:
            entries = [e for e in entries if e.entry_type == entry_type]
        return self.strategy.calculate(entries)

    def get_statistics(self, entry_type: EntryType) -> float:

        all_entries = self.repository.get_all()
        filtered_entries = [e for e in all_entries if e.entry_type == entry_type]
        return self.strategy.calculate(filtered_entries)

    def get_all_entries(self) -> List[HealthEntry]:
        return self.repository.get_all()