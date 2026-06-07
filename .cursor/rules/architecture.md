# Архітектура щоденника

Система побудована за принципами Чистої Архітектури (Clean Architecture):

1. **Domain Layer (`src/domain/`)**: Ентиті (`HealthEntry`), Енами (`EntryType`) та Інтерфейси (`IMoodRepository`). Це ядро системи.
2. **Application Layer (`src/application/`)**: Бізнес-логіка (`HealthService`) та аналітичні стратегії.
3. **Infrastructure Layer (`src/infrastructure/`)**: Реалізація репозиторіїв (файлове зберігання `data.json`).
4. **UI Layer (`src/ui/`)**: Інтерфейс на базі Flet.

Дані передаються через об'єкти моделей, сервіси не знають про спосіб зберігання (тільки через інтерфейси).