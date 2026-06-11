import uuid
from typing import List, Optional
from datetime import datetime
from src.domain.models import Reminder
from src.infrastructure.reminder_repositories import FileReminderRepository


class ReminderManager:
    def __init__(self, repository: FileReminderRepository):
        self.repository = repository
        self._reminders = self.repository.get_all()

    def create(self, text: str, due_date: datetime) -> Reminder:
        reminder = Reminder(id=str(uuid.uuid4()), text=text, due_date=due_date)
        self._reminders.append(reminder)
        self.repository.save_all(self._reminders)
        return reminder

    def get_all(self, include_completed: bool = True) -> List[Reminder]:
        filtered = self._reminders if include_completed else [r for r in self._reminders if not r.is_completed]
        return sorted(filtered, key=lambda r: r.due_date)

    def update(self, reminder_id: str, text: Optional[str] = None,
               due_date: Optional[datetime] = None, is_completed: Optional[bool] = None) -> bool:
        for r in self._reminders:
            if r.id == reminder_id:
                if text is not None: r.text = text
                if due_date is not None: r.due_date = due_date
                if is_completed is not None: r.is_completed = is_completed
                self.repository.save_all(self._reminders)
                return True
        return False

    def delete(self, reminder_id: str) -> bool:
        original_count = len(self._reminders)
        self._reminders = [r for r in self._reminders if r.id != reminder_id]
        return len(self._reminders) < original_count