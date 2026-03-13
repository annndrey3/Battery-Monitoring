# Тестирование проекта Battery Monitoring System

## Структура тестов

```
kursova/
├── backend/tests/
│   ├── __init__.py
│   ├── conftest.py              # Фикстуры pytest
│   ├── test_equipment.py        # Тесты оборудования
│   ├── test_batteries.py        # Тесты батарей
│   ├── test_measurements.py     # Тесты измерений
│   ├── test_incidents.py        # Тесты инцидентов
│   └── test_reports.py          # Тесты отчетов
│
└── frontend/tests/
    ├── setup.ts                 # Настройка тестового окружения
    ├── api.test.ts              # Тесты API
    ├── Layout.test.tsx          # Тесты компонента Layout
    └── EquipmentPage.test.tsx   # Тесты страницы Equipment
```

## Backend тесты (pytest)

### Установка зависимостей

```bash
cd backend
pip install -r requirements.txt
```

### Запуск тестов

```bash
# Все тесты
cd backend
pytest

# С подробным выводом
pytest -v

# С покрытием кода
pytest --cov=routers --cov=models --cov=database

# Конкретный файл
cd backend
pytest tests/test_equipment.py

# Конкретный тест
pytest tests/test_equipment.py::TestEquipmentAPI::test_create_equipment
```

### Что тестируется

**test_equipment.py** (15 тестов):
- Создание/получение/обновление/удаление оборудования
- Валидация полей (имя, тип, статус)
- Ошибки 404 для несуществующих записей

**test_batteries.py** (12 тестов):
- CRUD операции для батарей
- Фильтрация по оборудованию
- Валидация серийных номеров (уникальность)
- Проверка напряжения и емкости (> 0)

**test_measurements.py** (15 тестов):
- Создание измерений
- Получение истории по батарее
- Валидация температуры (≤ 80°C)
- Валидация заряда (0-100%)
- Валидация напряжения (> 0)
- Валидация тока (≥ 0)
- Автоматическое создание инцидентов

**test_incidents.py** (12 тестов):
- CRUD операции для инцидентов
- Фильтрация по типу и серьезности
- Решение инцидентов
- Валидация типов инцидентов

**test_reports.py** (10 тестов):
- Все 9 отчетных эндпоинтов
- Обработка пустой БД
- Отчеты для несуществующих батарей

## Frontend тесты (Vitest)

### Установка зависимостей

```bash
cd frontend
npm install
```

### Запуск тестов

```bash
# Все тесты
cd frontend
npm test

# С watch mode (перезапуск при изменениях)
npm test -- --watch

# С покрытием кода
npm test -- --coverage

# С UI интерфейсом
npm run test:ui
```

### Что тестируется

**Layout.test.tsx**:
- Отображение меню навигации
- Рендеринг outlet для страниц

**EquipmentPage.test.tsx**:
- Отображение заголовка и кнопки
- Открытие формы добавления
- Валидация обязательных полей

**api.test.ts**:
- Создание axios instance
- Корректная конфигурация

## Пример вывода backend тестов

```
$ pytest
============================== test session starts ==============================
platform win32 -- Python 3.10.0, pytest-7.4.3, pluggy-1.3.0
rootdir: d:\Prog\kursova\backend
configfile: pytest.ini
tests/test_equipment.py .................                                [ 29%]
tests/test_batteries.py ............                                    [ 48%]
tests/test_measurements.py ...............                              [ 70%]
tests/test_incidents.py ............                                    [ 88%]
tests/test_reports.py ..........                                        [100%]

============================== 64 passed in 2.34s ===============================
```

## Пример вывода frontend тестов

```
$ npm test
 ✓ tests/api.test.ts (1 test)
 ✓ tests/Layout.test.tsx (2 tests)
 ✓ tests/EquipmentPage.test.tsx (3 tests)

 Test Files  3 passed (3)
      Tests  6 passed (6)
   Duration  1.23s
```

## Интеграционное тестирование

Для полного тестирования системы:

1. Запустите backend:
   ```bash
   cd backend
   python main.py
   ```

2. В другом терминале запустите frontend тесты:
   ```bash
   cd frontend
   npm test
   ```

3. Или запустите e2e тесты (если настроены):
   ```bash
   npx playwright test
   ```

## Тестовые данные

Все backend тесты используют:
- SQLite in-memory базу данных (изолированную)
- Автоматическое создание/удаление таблиц для каждого теста
- Фикстуры для создания связанных данных

## CI/CD готовность

Тесты настроены для запуска в CI:

```yaml
# Пример GitHub Actions
name: Tests
on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: |
          cd backend
          pip install -r requirements.txt
          pytest

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: |
          cd frontend
          npm install
          npm test
```
