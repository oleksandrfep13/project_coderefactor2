import json
import os
from typing import List
from datetime import datetime
from src.domain.models import Reminder

class FileReminderRepository:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def _load(self) -> List[Reminder]:
        if not os.path.exists(self.file_path):
            return []
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [
                Reminder(
                    id=r['id'],
                    text=r['text'],
                    due_date=datetime.fromisoformat(r['due_date']),
                    is_completed=r.get('is_completed', False)
                ) for r in data
            ]

    def _save(self, reminders: List[Reminder]):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            data = [
                {
                    "id": r.id,
                    "text": r.text,
                    "due_date": r.due_date.isoformat(),
                    "is_completed": r.is_completed
                } for r in reminders
            ]
            json.dump(data, f, ensure_ascii=False, indent=4)

    def get_all(self) -> List[Reminder]:
        return self._load()

    def save_all(self, reminders: List[Reminder]):
        self._save(reminders)