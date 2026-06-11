from typing import List, Optional, Dict
from datetime import datetime
from src.domain.models import HealthEntry
from src.domain.interfaces import IMoodRepository

class InMemoryMoodRepository(IMoodRepository):
    def __init__(self):
        self._storage: Dict[str, HealthEntry] = {}

    def add(self, record: HealthEntry) -> None:
        self._storage[record.id] = record

    def get_all(self) -> List[HealthEntry]:
        return list(self._storage.values())

    def get_by_id(self, record_id: str) -> Optional[HealthEntry]:
        return self._storage.get(record_id)

    def get_by_date(self, date: datetime) -> List[HealthEntry]:
        return [r for r in self._storage.values() if r.timestamp.date() == date.date()]