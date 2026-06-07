import json
import os
from typing import List, Optional
from src.domain.models import HealthEntry, EntryType
from src.domain.interfaces import IMoodRepository
from datetime import datetime

class FileMoodRepository(IMoodRepository):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def add(self, record: HealthEntry) -> None:
        records = self.get_all()
        # Шукаємо, чи існує вже запис такого ж типу для такої ж дати
        existing_index = next(
            (i for i, r in enumerate(records)
             if r.entry_type == record.entry_type and r.timestamp.date() == record.timestamp.date()),
            None
        )

        if existing_index is not None:
            # Якщо запис є — оновлюємо його
            records[existing_index] = record
        else:
            # Якщо немає — додаємо новий
            records.append(record)

        # Зберігаємо оновлений список
        with open(self.file_path, 'w') as f:
            data = [
                {
                    "id": r.id,
                    "timestamp": r.timestamp.isoformat(),
                    "value": r.value,
                    "type": r.entry_type.value,
                    "note": r.note
                } for r in records
            ]
            json.dump(data, f)

    def get_all(self) -> List[HealthEntry]:
        if not os.path.exists(self.file_path):
            return []
        with open(self.file_path, 'r') as f:
            data = json.load(f)
            return [
                HealthEntry(
                    id=r['id'],
                    timestamp=datetime.fromisoformat(r['timestamp']),  # Перетворюємо рядок назад у дату
                    entry_type=EntryType(r['type']),
                    value=r['value'],
                    note=r['note']
                ) for r in data
            ]

    def get_by_id(self, record_id: str) -> Optional[HealthEntry]:
        return next((r for r in self.get_all() if r.id == record_id), None)


    def get_by_date(self, date: datetime) -> List[HealthEntry]:
        all_records = self.get_all()
        return [r for r in all_records if r.timestamp.date() == date.date()]