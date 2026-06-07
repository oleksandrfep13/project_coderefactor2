from typing import List, Optional, Dict
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