from src.infrastructure.repositories import InMemoryMoodRepository
from src.application.services import MoodService

# DI: передаємо реалізацію в сервіс
repo = InMemoryMoodRepository()
service = MoodService(repo)

# Використання
service.create_mood_record(5, "Чудовий день!")
print(f"Середній настрій: {service.get_statistics()}")