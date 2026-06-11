from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from .models import HealthEntry


class IMoodRepository(ABC):


    @abstractmethod
    def add(self, record: HealthEntry) -> None:
        pass

    @abstractmethod
    def get_all(self) -> List[HealthEntry]:
        pass

    @abstractmethod
    def get_by_id(self, record_id: str) -> Optional[HealthEntry]:
        pass

    @abstractmethod
    def get_by_date(self, date: datetime) -> List[HealthEntry]:
        pass