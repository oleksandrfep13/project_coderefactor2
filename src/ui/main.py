import flet as ft
from datetime import datetime, timedelta
from src.application.services import HealthService
from src.application.reminder import ReminderManager
from src.infrastructure.file_repositories import FileMoodRepository
from src.infrastructure.reminder_repositories import FileReminderRepository
from src.application.analytics import AverageMoodStrategy, VolatilityStrategy, StabilityStrategy, ExtremeValueStrategy
from src.domain.models import EntryType

def main(page: ft.Page, service: HealthService = None, rem_manager: ReminderManager = None):
    page.clean()
    page.title = "Мій щоденник"
    page.scroll = ft.ScrollMode.AUTO

    if service is None:
        repo = FileMoodRepository("data.json")
        rem_repo = FileReminderRepository("reminders.json")
        rem_manager = ReminderManager(rem_repo)
        service = HealthService(repo, AverageMoodStrategy())

    view_date = datetime.now()
    date_text = ft.Text(view_date.strftime('%d.%m.%Y'), size=25, weight="bold")
    mood_input = ft.TextField(label="Настрій (1-5)", keyboard_type=ft.KeyboardType.NUMBER)
    mood_note = ft.TextField(label="Пояснення настрою")
    health_input = ft.TextField(label="Здоров'я (1-5)", keyboard_type=ft.KeyboardType.NUMBER)
    health_note = ft.TextField(label="Пояснення стану здоров'я")

    def save_data(e):
        try:
            if mood_input.value:
                service.add_entry(EntryType.MOOD, float(mood_input.value), mood_note.value, view_date)
            if health_input.value:
                service.add_entry(EntryType.HEALTH, float(health_input.value), health_note.value, view_date)
            page.show_snack_bar(ft.SnackBar(ft.Text("Успішно збережено!")))
            page.update()
        except ValueError as err:
            page.show_snack_bar(ft.SnackBar(ft.Text(str(err), color="red")))
            page.update()

    save_btn = ft.FilledButton("Зберегти записи", on_click=save_data)

    def update_date(delta):
        nonlocal view_date
        view_date += timedelta(days=delta)
        date_text.value = view_date.strftime('%d.%m.%Y')
        save_btn.disabled = not (view_date.date() == datetime.now().date())
        load_data_for_date(view_date)

    def show_reminder_view(page, service, rem_manager, reminder_to_edit=None):
        is_edit = reminder_to_edit is not None

        text_input = ft.TextField(label="Текст нагадування", value=reminder_to_edit.text if is_edit else "")
        date_picker = ft.DatePicker(first_date=datetime.now())
        page.overlay.append(date_picker)

        date_btn = ft.FilledButton(
            f"Дата: {reminder_to_edit.due_date.strftime('%d.%m.%Y')}" if is_edit else "Вибрати дату",
            on_click=lambda _: setattr(date_picker, 'open', True) or page.update()
        )

        def save_reminder(e):
            if text_input.value and (date_picker.value or is_edit):
                selected_date = date_picker.value or reminder_to_edit.due_date

                if is_edit:
                    rem_manager.update(reminder_to_edit.id, text=text_input.value, due_date=selected_date)
                else:
                    rem_manager.create(text_input.value, selected_date)

                show_reminders_list(page, service, rem_manager)

        page.clean()
        page.add(
            ft.Text("Редагування" if is_edit else "Нове нагадування", size=20, weight="bold"),
            text_input, date_btn,
            ft.FilledButton("Зберегти", on_click=save_reminder),
            ft.OutlinedButton("Назад", on_click=lambda _: show_reminders_list(page, service, rem_manager))
        )
        page.update()

    def show_reminders_list(page, service, rem_manager):
        def refresh():
            show_reminders_list(page, service, rem_manager)

        page.clean()
        page.add(ft.Text("Мої нагадування", size=20, weight="bold"))

        for r in rem_manager.get_all():
            page.add(ft.ListTile(
                title=ft.Text(r.text),
                subtitle=ft.Text(r.due_date.strftime('%d.%m.%Y')),
                leading=ft.Container(
                    content=ft.Text("✏️", size=20),
                    on_click=lambda e, rem=r: show_reminder_view(page, service, rem_manager, rem),
                    padding=5
                ),
                trailing=ft.Container(
                    content=ft.Text("❌", size=20),
                    on_click=lambda e, id=r.id: (rem_manager.delete(id), refresh()),
                    padding=5
                )
            ))

        page.add(ft.FilledButton("Назад", on_click=lambda e: main(page, service, rem_manager)))
        page.update()

    def load_data_for_date(date):
        entries = service.repository.get_by_date(date)
        mood_input.value = mood_note.value = health_input.value = health_note.value = ""
        for e in entries:
            if e.entry_type == EntryType.MOOD: mood_input.value, mood_note.value = str(e.value), e.note
            if e.entry_type == EntryType.HEALTH: health_input.value, health_note.value = str(e.value), e.note
        page.update()

    page.add(
        ft.Row([ft.TextButton("<", on_click=lambda e: update_date(-1)), date_text, ft.TextButton(">", on_click=lambda e: update_date(1))], alignment=ft.MainAxisAlignment.CENTER),
        mood_input, mood_note, health_input, health_note, save_btn,
        ft.PopupMenuButton(
            icon="notifications",
            items=[
                ft.PopupMenuItem(
                    "Створити",
                    icon="add_box",
                    on_click=lambda e: show_reminder_view(page, service, rem_manager)
                ),
                ft.PopupMenuItem(
                    "Список",
                    icon="list",
                    on_click=lambda e: show_reminders_list(page, service, rem_manager)
                ),
            ]
        ),
        ft.FilledButton("Статистика", on_click=lambda e: ... )
    )
    load_data_for_date(view_date)

if __name__ == "__main__":
    ft.run(main)