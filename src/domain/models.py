from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional

class EntryType(Enum):
    MOOD = "mood"
    HEALTH = "health"

@dataclass
class HealthEntry:
    id: str
    timestamp: datetime
    entry_type: EntryType
    value: float
    note: str
    metadata: dict = field(default_factory=dict)

@dataclass
class Reminder:
    id: str
    text: str
    due_date: datetime
    is_completed: bool = False