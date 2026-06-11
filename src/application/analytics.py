from abc import ABC, abstractmethod
from typing import List
from src.domain.models import HealthEntry, EntryType
from datetime import datetime, timedelta


class IAnalyticsStrategy(ABC):
    @abstractmethod
    def calculate(self, records: List[HealthEntry]) -> float:
        pass

class AverageMoodStrategy(IAnalyticsStrategy):
    def calculate(self, records: List[HealthEntry]) -> float:
        if not records:
            return 0.0
        return round(sum(r.value for r in records) / len(records), 2)

class VolatilityStrategy(IAnalyticsStrategy):
    def calculate(self, records: List[HealthEntry]) -> float:
        if len(records) < 2:
            return 0.0
        diffs = [abs(records[i].value - records[i-1].value) for i in range(1, len(records))]
        return round(sum(diffs) / len(diffs), 2)

class RecentTrendStrategy(IAnalyticsStrategy):
    def calculate(self, entries: List[HealthEntry]) -> float:
        if not entries:
            return 0.0

        now = datetime.now()
        time_limit = timedelta(days=7, seconds=1)

        recent_entries = [
            e for e in entries
            if (now - e.timestamp) <= time_limit
        ]

        if not recent_entries:
            return 0.0

        return sum(e.value for e in recent_entries) / len(recent_entries)

class StabilityStrategy(IAnalyticsStrategy):
    def calculate(self, records: List[HealthEntry]) -> float:
        if not records: return 0.0
        avg = sum(r.value for r in records) / len(records)
        variance = sum((r.value - avg) ** 2 for r in records) / len(records)
        return round(variance ** 0.5, 2)

class ExtremeValueStrategy(IAnalyticsStrategy):
    def calculate(self, records: List[HealthEntry]) -> float:
        if not records: return 0.0
        return float(max(r.value for r in records) - min(r.value for r in records))