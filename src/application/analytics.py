from abc import ABC, abstractmethod
from typing import List
from src.domain.models import HealthEntry


class IAnalyticsStrategy(ABC):
    @abstractmethod
    def calculate(self, records: List[HealthEntry]) -> float:
        pass


class AverageMoodStrategy(IAnalyticsStrategy):
    def calculate(self, records: List[HealthEntry]) -> float:
        if not records:
            return 0.0
        return sum(r.value for r in records) / len(records)


class RecentTrendStrategy(IAnalyticsStrategy):
    def calculate(self, records: List[HealthEntry]) -> float:
        if len(records) < 2:
            return 0.0
        recent = records[-7:]
        return sum(r.value for r in recent) / len(recent)