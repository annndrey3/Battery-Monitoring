# Battery Monitoring System 🔋

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

> Система моніторингу стану батарей автономного обладнання з AI-аналітикою

## 🚀 Особливості

- **📊 Моніторинг в реальному часі** — відстеження рівня заряду, температури, напруги та струму
- **🤖 AI Аналіз** — інтелектуальний аналіз стану батарей через Google Gemini API
- **📈 Візуалізація даних** — інтерактивні графіки та звіти
- **🔔 Сповіщення** — автоматичне створення інцидентів при критичних значеннях
- **🌐 Публічний доступ** — підтримка ngrok для доступу ззовні
- **📱 Адаптивний дизайн** — підтримка мобільних пристроїв

## 🛠 Технологічний стек

### Backend
- **Python 3.11+**
- **FastAPI** — сучасний високопродуктивний веб-фреймворк
- **SQLAlchemy** — ORM для роботи з базою даних
- **PostgreSQL** — реляційна база даних
- **Google Generative AI** — інтеграція з Gemini API
- **Uvicorn** — ASGI сервер

### Frontend
- **React 18**
- **TypeScript**
- **Tailwind CSS**
- **Vite**
- **Recharts**
- **Axios**

## 📁 Структура проекту

```
battery-monitoring/
├── backend/              # FastAPI бекенд
│   ├── database/
│   ├── routers/
│   ├── services/
│   └── requirements.txt
├── frontend/             # React фронтенд
│   └── src/
├── database/             # SQL схема
├── docs/                 # Документація
├── .env.example          # Шаблон змінних
└── docker-compose.yml    # Docker конфігурація
```

## 🚀 Швидкий старт

### 1. Клонування та налаштування

```bash
git clone https://github.com/yourusername/battery-monitoring.git
cd battery-monitoring

# Скопіюйте шаблон змінних середовища
cp .env.example .env
# Відредагуйте .env та додайте свої ключі API
```

### 2. Автоматичне встановлення (Windows)

```bash
setup.bat
```

### 3. Запуск

```bash
# Локальний запуск
start-all.bat

# З публічним URL через ngrok
start-with-ngrok.bat
```

Або вручну:

```bash
# Backend
cd backend
uvicorn main:app --reload

# Frontend (в новому терміналі)
cd frontend
npm run dev
```

## 🔧 Конфігурація

### Змінні середовища (.env)

| Змінна | Опис | Обов'язкова |
|--------|------|-------------|
| `DATABASE_URL` | URL PostgreSQL | Так |
| `SECRET_KEY` | JWT секрет | Так |
| `GEMINI_API_KEY` | Google Gemini API | Ні |
| `NGROK_AUTHTOKEN` | Ngrok токен | Ні |

## 📊 Функціональність

- 📈 Моніторинг рівня заряду в реальному часі
- 🌡️ Контроль температури (сповіщення при >60°C)
- 🤖 AI аналіз стану системи (Google Gemini)
- 📊 Історичні дані та тренди
- 📋 Звіти та аналітика
- 🔔 Журнал інцидентів

## 🌐 Ngrok інтеграція

Для публічного доступу:
1. Отримайте токен на [ngrok.com](https://dashboard.ngrok.com)
2. Додайте в `.env`: `NGROK_AUTHTOKEN=your_token`
3. Запустіть: `start-with-ngrok.bat`

## 🧪 API Документація

- 📚 Swagger UI: http://localhost:8000/docs
- 📖 ReDoc: http://localhost:8000/redoc

## 📄 Ліцензія

MIT License

---

⭐ Не забудьте поставити зірку, якщо проект був корисним!
