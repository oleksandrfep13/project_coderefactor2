from abc import ABC, abstractmethod
from typing import List, Optional
from .models import HealthEntry

class IMoodRepository(ABC):
    @abstractmethod
    def add(self, record: HealthEntry) -> None: # І тут
        pass

    @abstractmethod
    def get_all(self) -> List[HealthEntry]: # І тут
        pass

    @abstractmethod
    def get_by_id(self, record_id: str) -> Optional[HealthEntry]: # І тут
        pass