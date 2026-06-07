import uuid
import flet as ft
import threading
import time
from datetime import datetime, timedelta
from src.application.services import HealthService
from src.infrastructure.file_repositories import FileMoodRepository
from src.application.analytics import AverageMoodStrategy
from src.domain.models import EntryType, HealthEntry


def reminder_worker(page):
    while True:
        now = datetime.now()
        # Для перевірки працездатності: кожні 30 секунд (замість 20:00)
        if now.hour == 20 and now.minute == 0:
            page.show_snack_bar(ft.SnackBar(ft.Text("Час заповнити щоденник!")))
            page.update()
            time.sleep(60)
        time.sleep(30)



def main(page: ft.Page):
    # Очищуємо сторінку при кожному виклику main, щоб уникнути нашарування
    page.clean()

    page.title = "Мій щоденник"
    page.scroll = ft.ScrollMode.AUTO

    repo = FileMoodRepository("data.json")
    service = HealthService(repo, AverageMoodStrategy())

    view_date = datetime.now()

    date_text = ft.Text(view_date.strftime('%d.%m.%Y'), size=25, weight="bold")
    mood_input = ft.TextField(label="Настрій (1-5)", keyboard_type=ft.KeyboardType.NUMBER)
    mood_note = ft.TextField(label="Пояснення настрою")
    health_input = ft.TextField(label="Здоров'я (1-5)", keyboard_type=ft.KeyboardType.NUMBER)
    health_note = ft.TextField(label="Пояснення стану здоров'я")
    reminder_thread = threading.Thread(target=reminder_worker, args=(page,), daemon=True)
    reminder_thread.start()

    def update_date(delta):
        nonlocal view_date
        view_date += timedelta(days=delta)
        date_text.value = view_date.strftime('%d.%m.%Y')
        load_data_for_date(view_date)

    def save_data(e):
        try:
            if mood_input.value:
                entry = HealthEntry(
                    id=str(uuid.uuid4()),
                    timestamp=view_date,
                    entry_type=EntryType.MOOD,
                    value=float(mood_input.value),
                    note=mood_note.value
                )
                service.repository.add(entry)

            if health_input.value:
                entry = HealthEntry(
                    id=str(uuid.uuid4()),
                    timestamp=view_date,
                    entry_type=EntryType.HEALTH,
                    value=float(health_input.value),
                    note=health_note.value
                )
                service.repository.add(entry)

            date_text.value = f"Збережено для {view_date.strftime('%d.%m.%Y')}"
            page.update()
        except ValueError:
            pass

    def load_data_for_date(date):
        entries = repo.get_by_date(date)
        mood_input.value = ""
        mood_note.value = ""
        health_input.value = ""
        health_note.value = ""
        for entry in entries:
            if entry.entry_type == EntryType.MOOD:
                mood_input.value = str(entry.value)
                mood_note.value = entry.note
            elif entry.entry_type == EntryType.HEALTH:
                health_input.value = str(entry.value)
                health_note.value = entry.note
        page.update()

    def show_statistics(page, service):
        entries = service.get_all_entries()
        mood_entries = [e for e in entries if e.entry_type == EntryType.MOOD]
        health_entries = [e for e in entries if e.entry_type == EntryType.HEALTH]

        avg_mood = sum(e.value for e in mood_entries) / len(mood_entries) if mood_entries else 0
        avg_health = sum(e.value for e in health_entries) / len(health_entries) if health_entries else 0

        stats_list = [
            ft.ListTile(
                title=ft.Text(f"{e.timestamp.strftime('%d.%m')} - {e.entry_type.name}"),
                subtitle=ft.Text(f"Оцінка: {e.value} | {e.note}")
            ) for e in entries
        ]

        page.clean()
        page.add(
            ft.Text("Аналітика", size=25, weight="bold"),
            ft.Text(f"Середній настрій: {avg_mood:.2f}"),
            ft.Text(f"Середнє здоров'я: {avg_health:.2f}"),
            ft.Divider(),
            ft.Column(stats_list, scroll=ft.ScrollMode.AUTO, height=400),
            ft.FilledButton("Назад", on_click=lambda e: main(page))
        )
        page.update()

    # Початковий вигляд головної сторінки
    page.add(
        ft.Row([
            ft.TextButton("Попередня", on_click=lambda e: update_date(-1)),
            date_text,
            ft.TextButton("Наступна", on_click=lambda e: update_date(1))
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Divider(),
        mood_input,
        mood_note,
        ft.Divider(),
        health_input,
        health_note,
        ft.FilledButton("Зберегти записи", on_click=save_data),
        ft.FilledButton("Статистика", on_click=lambda e: show_statistics(page, service))
    )
    load_data_for_date(view_date)


if __name__ == "__main__":
    ft.app(target=main)