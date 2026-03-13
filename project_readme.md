# Система мониторинга батарей автономного оборудования

Курсовая работа по дисциплине **"Базы данных измерительной информации"**

**Тема:** №20 Мониторинг состояния батарей автономного оборудования

---

## Технологический стек

**Backend:**
- Python 3.11+
- FastAPI (REST API)
- SQLAlchemy (ORM)
- PostgreSQL
- Uvicorn (ASGI сервер)

**Frontend:**
- React 18
- TypeScript
- Tailwind CSS
- Recharts (графики)
- Vite (сборка)
- Axios (HTTP клиент)

---

## Установка и запуск

### 1. База данных PostgreSQL

```bash
# Создание базы данных
createdb battery_monitoring

# Выполнение схемы
psql -d battery_monitoring -f database/schema.sql
```

Конфигурация подключения в `backend/database/database.py`:
```python
DATABASE_URL = "postgresql://postgres:postgres@localhost/battery_monitoring"
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

- API доступен на: `http://localhost:8000`
- Swagger документация: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

- Приложение откроется на: `http://localhost:3000`
- API проксируется через Vite

---

## Структура базы данных

### ER модель
```
Equipment (1) ───< (N) Batteries (1) ───< (N) Measurements (1) ───< (N) Incidents
                          ↑
                    Users (measured_by, resolved_by)
```

### Таблицы

| Таблица | Описание | Поля |
|---------|----------|------|
| **users** | Пользователи системы | id, username, password_hash, role, full_name, created_at |
| **equipment** | Оборудование | id, name, type, location, description, status, created_at |
| **batteries** | Аккумуляторы | id, equipment_id, serial_number, capacity, voltage_nominal, install_date, status |
| **measurements** | Измерения | id, battery_id, voltage, current, charge_level, temperature, timestamp, measured_by |
| **incidents** | Журнал инцидентов | id, measurement_id, battery_id, incident_type, description, severity, is_resolved, created_at |

### Нормализация (3NF)
- **1NF:** Все атрибуты атомарные
- **2NF:** Отсутствуют частичные функциональные зависимости
- **3NF:** Отсутствуют транзитивные зависимости

### Триггеры
- Автоматическое обновление `updated_at` для Equipment и Batteries
- Автоматическое создание инцидентов при критических значениях:
  - Температура > 60°C → инцидент "overheat"
  - Заряд < 20% → инцидент "low_charge"
  - Напряжение вне диапазона 10-15V → инцидент "voltage_spike"

---

## API Endpoints

### Оборудование
```
GET    /equipment              # Список оборудования
GET    /equipment/{id}         # Детали оборудования
POST   /equipment              # Добавить оборудование
PUT    /equipment/{id}         # Обновить
DELETE /equipment/{id}         # Удалить
```

### Батареи
```
GET    /batteries              # Список батарей
GET    /batteries/{id}         # Детали батареи
POST   /batteries              # Добавить батарею
PUT    /batteries/{id}         # Обновить
DELETE /batteries/{id}         # Удалить
```

### Измерения
```
GET    /measurements           # Список измерений
GET    /measurements/{id}      # Детали измерения
POST   /measurements           # Добавить измерение
GET    /measurements/history/{battery_id}  # История по батарее
DELETE /measurements/{id}      # Удалить
```

### Инциденты
```
GET    /incidents              # Список инцидентов
GET    /incidents/{id}         # Детали инцидента
POST   /incidents              # Создать инцидент
PUT    /incidents/{id}         # Обновить (решить)
```

### Отчеты
```
GET /reports/charge-levels        # Уровни заряда по оборудованию
GET /reports/temperature-alerts   # Критические температуры
GET /reports/voltage-deviation    # Отклонение напряжения
GET /reports/incident-stats       # Статистика инцидентов
GET /reports/equipment-incidents  # Оборудование с инцидентами
GET /reports/current-stats        # Статистика по току
GET /reports/equipment-measurements # Измерения по оборудованию
GET /reports/battery-discharge/{id} # График разряда
GET /reports/temperature-chart/{id} # Температурный график
```

---

## SQL Запросы (10 сложных)

Все запросы находятся в `database/queries.sql`:

1. **Средний уровень заряда батарей по оборудованию** — агрегация с группировкой
2. **Поиск батарей с критической температурой** — фильтрация с CASE
3. **История измерений батареи с агрегацией по часам** — временные окна
4. **Статистика инцидентов по типам и месяцам** — группировка по периодам
5. **Среднее напряжение батарей с отклонением от номинала** — математические вычисления
6. **Оборудование с наибольшим количеством инцидентов** — агрегация с JOIN
7. **Максимальная температура батареи с детализацией** — подзапросы
8. **Минимальный уровень заряда с прогнозом** — сложные вычисления
9. **Средний ток с группировкой по диапазонам** — CASE в агрегации
10. **Количество измерений по оборудованию с активностью операторов** — множественные JOIN

---

## Интерфейс пользователя

### Страницы (6 форм)
1. **Dashboard** — главная панель со статистикой и графиками
2. **Оборудование** — управление оборудованием (CRUD)
3. **Батареи** — управление батареями (CRUD)
4. **Измерения** — ввод показателей с валидацией
5. **Инциденты** — журнал инцидентов с фильтрацией
6. **Отчеты** — аналитика и графики

### Валидация данных (frontend + backend)
- Температура: ≤ 80°C
- Уровень заряда: 0-100%
- Напряжение: > 0
- Ток: ≥ 0

### Графики и отчеты (5 видов)
1. График разряда батареи (заряд + напряжение)
2. Температурный график (min/avg/max)
3. Таблица инцидентов с фильтрами
4. Статистика батарей (уровень заряда)
5. Подсумочный отчет по оборудованию

---

## Структура проекта

```
kursova/
├── backend/
│   ├── main.py                 # Точка входа FastAPI
│   ├── requirements.txt        # Зависимости Python
│   ├── database/
│   │   ├── __init__.py
│   │   └── database.py         # SQLAlchemy подключение
│   ├── models/
│   │   ├── __init__.py
│   │   ├── models.py           # ORM модели
│   │   └── schemas.py          # Pydantic схемы
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── equipment.py        # API оборудования
│   │   ├── batteries.py        # API батарей
│   │   ├── measurements.py     # API измерений
│   │   ├── incidents.py        # API инцидентов
│   │   └── reports.py          # API отчетов
│   └── services/
│       └── __init__.py
│
├── frontend/
│   ├── index.html
│   ├── package.json            # Зависимости Node.js
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── src/
│       ├── main.tsx            # Точка входа React
│       ├── App.tsx             # Маршрутизация
│       ├── index.css           # Tailwind стили
│       ├── components/
│       │   └── Layout.tsx      # Навигация
│       ├── pages/
│       │   ├── Dashboard.tsx   # Главная страница
│       │   ├── EquipmentPage.tsx
│       │   ├── BatteriesPage.tsx
│       │   ├── MeasurementsPage.tsx
│       │   ├── IncidentsPage.tsx
│       │   └── ReportsPage.tsx
│       └── services/
│           └── api.ts          # HTTP клиент
│
└── database/
    ├── schema.sql              # Схема БД (триггеры, индексы)
    └── queries.sql             # 10 сложных SQL запросов
```

---

## Зависимости

### Backend (requirements.txt)
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
python-multipart==0.0.6
```

### Frontend (package.json)
```
react: ^18.2.0
typescript: ^5.3.3
tailwindcss: ^3.3.6
recharts: ^2.10.3
axios: ^1.6.2
vite: ^5.0.8
```

---

## Пользователи системы

| Роль | Возможности |
|------|-------------|
| **Оператор** | Добавление оборудования, ввод измерений, просмотр показателей |
| **Инженер** | Анализ параметров, просмотр истории, отчеты |
| **Администратор** | Полный контроль системы, управление БД |

---

## Особенности реализации

- **Клиент-серверная архитектура** — React SPA + FastAPI REST
- **CORS** — настроен для разработки (localhost:3000)
- **Автоматические инциденты** — триггер БД создает записи при критических значениях
- **Респонсивный дизайн** — Tailwind CSS, мобильная адаптация
- **Типизация** — полная типизация TypeScript на frontend

---

## Разработка

Проект создан с использованием:
- Windsurf IDE с AI помощником Cascade
- PostgreSQL 15+
- Node.js 18+
- Python 3.11+
