# Інструкція з розгортання системи

## Система моніторингу стану батарей автономного обладнання

---

## Вимоги до системи

### Апаратні вимоги
- CPU: 2+ ядра
- RAM: 4+ GB
- Disk: 10+ GB вільного місця

### Програмні вимоги
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Git

---

## 1. Встановлення PostgreSQL

### Windows

1. Завантажте PostgreSQL з https://www.postgresql.org/download/windows/
2. Встановіть з параметрами за замовчуванням
3. Запам'ятайте пароль користувача `postgres`
4. Переконайтесь, що порт 5432 вільний

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### macOS

```bash
brew install postgresql
brew services start postgresql
```

---

## 2. Створення бази даних

```bash
# Перейдіть до користувача postgres
sudo -u postgres psql

# У консолі psql виконайте:
CREATE DATABASE battery_monitoring;
CREATE USER battery_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE battery_monitoring TO battery_user;

# Вийдіть
\q
```

---

## 3. Клонування проекту

```bash
git clone <repository-url>
cd battery-monitoring
```

---

## 4. Налаштування Backend

### 4.1. Створення віртуального середовища

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 4.2. Встановлення залежностей

```bash
pip install -r requirements.txt
```

### 4.3. Налаштування змінних середовища

Створіть файл `.env` у папці `backend`:

```env
DATABASE_URL=postgresql://battery_user:your_password@localhost/battery_monitoring
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4.4. Виконання міграцій

```bash
# Ініціалізація Alembic (вже виконано у проекті)
# alembic init alembic

# Створення першої міграції
alembic revision --autogenerate -m "Initial migration"

# Застосування міграцій
alembic upgrade head
```

### 4.5. Запуск сервера

```bash
# Режим розробки з автоматичним перезавантаженням
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Режим production
uvicorn main:app --host 0.0.0.0 --port 8000
```

Сервер буде доступний за адресою: http://localhost:8000

Документація API: http://localhost:8000/docs

---

## 5. Налаштування Frontend

### 5.1. Встановлення залежностей

```bash
cd frontend
npm install
```

### 5.2. Налаштування API URL

За замовчуванням frontend очікує API за адресою http://localhost:8000

При необхідності змініть у файлі `frontend/src/services/api.ts`:

```typescript
const API_URL = 'http://localhost:8000' // або ваш URL
```

### 5.3. Запуск development сервера

```bash
npm run dev
```

Сервер буде доступний за адресою: http://localhost:3000

### 5.4. Збірка для production

```bash
npm run build
```

Статичні файли будуть у папці `dist/`.

---

## 6. Запуск тестів

### Backend тести

```bash
cd backend
pytest -v
```

### Frontend тести

```bash
cd frontend
npm test -- --run
```

---

## 6. Публичный доступ через Ngrok (опционально)

Ngrok позволяет получить публичный URL для доступа к проекту из интернета.

### 6.1. Получение токена

1. Зарегистрируйтесь на https://ngrok.com
2. Получите токен: https://dashboard.ngrok.com/get-started/your-authtoken

### 6.2. Настройка

```bash
# Создайте файл .env в корне проекта
cp .env.example .env

# Отредактируйте .env и добавьте ваш токен
NGROK_AUTHTOKEN=your_actual_token_here
```

### 6.3. Запуск с ngrok

```bash
# Запуск всех сервисов + ngrok
docker-compose --profile ngrok up -d

# Только ngrok (если остальные сервисы уже запущены)
docker-compose --profile ngrok up -d ngrok
```

### 6.4. Получение публичного URL

```bash
# Просмотр логов ngrok
docker-compose logs ngrok

# Или откройте в браузере
curl http://localhost:4040/api/tunnels
```

Публичный URL будет вида: `https://xxxx.ngrok.io`

### 6.5. Web-интерфейс ngrok

Доступен по адресу: http://localhost:4040

---

## 7. Налаштування production

### 7.1. PostgreSQL

Рекомендації для production:
- Встановити strong password для postgres
- Налаштувати firewall (доступ тільки з localhost)
- Увімкнути SSL
- Налаштувати regular backups

### 7.2. Backend

Рекомендації:
- Використовувати Gunicorn замість uvicorn
- Налаштувати reverse proxy (Nginx)
- Увімкнути HTTPS
- Налаштувати логування

```bash
# Запуск з Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 7.3. Frontend

Рекомендації:
- Використовувати Nginx для роздачі статичних файлів
- Увімкнути gzip compression
- Налаштувати caching

Приклад Nginx конфігурації:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /path/to/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 8. Docker (опціонально)

### 8.1. Збірка образів

```bash
docker-compose build
```

### 8.2. Запуск

```bash
docker-compose up -d
```

### 8.3. Зупинка

```bash
docker-compose down
```

---

## 9. Вирішення проблем

### Проблема: Порт 8000 або 3000 зайнятий

```bash
# Windows - знайти та зупинити процес
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS
lsof -ti:8000 | xargs kill -9
```

### Проблема: Помилка підключення до PostgreSQL

1. Перевірте, що PostgreSQL запущено:
   ```bash
   sudo systemctl status postgresql
   ```

2. Перевірте налаштування у `.env` файлі

3. Перевірте firewall налаштування

### Проблема: Помилки CORS

Переконайтесь, що CORS налаштовано правильно у `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    ...
)
```

---

## 10. Структура проекту

```
battery-monitoring/
├── backend/
│   ├── alembic/              # Міграції
│   ├── models/               # SQLAlchemy моделі
│   ├── routers/              # API роутери
│   ├── tests/                # Тести
│   ├── main.py              # Точка входу
│   └── requirements.txt     # Залежності
├── frontend/
│   ├── src/
│   │   ├── components/      # React компоненти
│   │   ├── pages/          # Сторінки
│   │   └── services/       # API сервіси
│   ├── tests/              # Тести
│   └── package.json        # Залежності
├── database/
│   ├── schema.sql          # SQL схема
│   └── queries.sql         # Аналітичні запити
├── docs/
│   └── report.md           # Пояснювальна записка
└── README.md               # Загальний опис
```

---

## Підтримка

При виникненні проблем звертайтесь до:
- Документації API: http://localhost:8000/docs
- FASTAPI docs: https://fastapi.tiangolo.com/
- React docs: https://react.dev/

---

**Успішного розгортання!**
