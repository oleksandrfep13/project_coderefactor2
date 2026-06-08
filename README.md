# МОБІЛЬНИЙ щоденник настрою і здоров'я

Цей проєкт — аналітичний застосунок для відстеження стану здоров'я та настрою користувача. Проєкт реалізований з дотриманням принципів Clean Architecture, SOLID та використанням автоматизованих тестів.

## Технології
* **Мова:** Python 3.12+
* **UI Framework:** Flet (Material Design)
* **Тестування:** pytest, pytest-cov
* **Аналіз якості:** SonarCloud
* **CI/CD:** GitHub Actions

## Архітектура
Проєкт побудований за принципами чистої архітектури:
- **Domain:** Бізнес-сутності (HealthEntry, EntryType).
- **Application:** Бізнес-логіка (HealthService, AnalyticsStrategy).
- **Infrastructure:** Робота з даними (FileMoodRepository).
- **UI:** Інтерфейс користувача (Flet).

## DevOps та CI/CD
Проєкт інтегрований із SonarCloud для автоматичного контролю якості коду.
- **Quality Gate:** Покриття коду >70%.
- **Branch Protection:** Заборона злиття до гілки `main` без успішного проходження тестів.

### Локальне розгортання
```bash
# Клонування репозиторію
git clone [https://github.com/oleksandrfep13/project_coderefactor2.git](https://github.com/oleksandrfep13/project_coderefactor2.git)
cd project_coderefactor2

# Створення віртуального середовища та встановлення залежностей
python -m venv venv
source venv/bin/activate  # Для Windows: venv\Scripts\activate
pip install -r requirements.txt

# Запуск тестів
pytest
