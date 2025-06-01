# Gidrator

## Установка

Клонируйте репозиторий в директорию, в которой находитесь:
```bash
git clone https://gitlab.com/store-be/gidrator-be.git .
```
Или:
```bash
git clone https://gitlab.com/store-be/gidrator-be.git
```
Перейдите в директорию с проектом:
```bash
cd ./gidrator-be
```

> [!NOTE]
> Перед тем, как запускать проект, проверьте наличие файла `.env`

## Настройка окружения

Перед запуском проекта необходимо настроить переменные окружения.
В проекте используется файл `.env.dev` для разработки.

Скопируйте пример конфигурации из .env.example в новый файл .env.dev:
```bash
cp .env.example .env.dev
```

Отредактируйте файл .env.dev, заполнив следующие обязательные параметры:

### Настройки JWT и безопасности
- `TOKEN_SECRET_KEY` - секретный ключ для подписи JWT токенов (обязательно!)
- `COOKIE_DOMAIN` - домен для cookies (localhost для разработки)

### Настройки базы данных PostgreSQL
- `POSTGRES_USER` - имя пользователя PostgreSQL
- `POSTGRES_PASSWORD` - пароль пользователя PostgreSQL
- `POSTGRES_HOST` - хост базы данных (обычно localhost для разработки)
- `POSTGRES_PORT` - порт PostgreSQL (по умолчанию 5432)
- `POSTGRES_DB` - имя базы данных

### Настройки Redis
- `REDIS_PASSWORD` - пароль для Redis
- `REDIS_PORT` - порт Redis (по умолчанию 6379)

### Настройки RabbitMQ
- `RABBITMQ_USER` - имя пользователя RabbitMQ
- `RABBITMQ_PASS` - пароль пользователя RabbitMQ
- `RABBITMQ_HOST` - хост RabbitMQ
- `RABBITMQ_PORT` - порт RabbitMQ (по умолчанию 5672)
- `RABBITMQ_EXCHANGE` - имя exchange для сообщений

### Настройки SMTP (для отправки email)
- `SMTP_USERNAME` - имя пользователя SMTP
- `SMTP_PASSWORD` - пароль SMTP
- `SMTP_PORT` - порт SMTP (по умолчанию 587)

### Настройки CORS
- `ALLOW_ORIGINS` - список разрешенных источников (для разработки обычно ["*"])

### Настройки логирования
- `LOGGING__LOG_FORMAT` - формат логов (pretty/json)
- `LOGGING__LOG_FILE` - путь к файлу логов
- `LOGGING__LEVEL` - уровень логирования (DEBUG/INFO/WARNING/ERROR)

> [!NOTE]
> Порт 5432 может быть занят, поэтому его можно изменить на любой другой свободный порт (например, 5433).
>
>
### Настройки CORS
- `ALLOW_ORIGINS` - список разрешенных источников (для разработки обычно ["http://localhost:3000","http://localhost:5173"])

### Пример минимальной конфигурации для локальной разработки
# Настройки логирования
LOGGING__LOG_FORMAT=pretty
LOGGING__LOG_FILE=./logs/app.log
LOGGING__LEVEL=DEBUG

# Настройки JWT (ОБЯЗАТЕЛЬНО!)
TOKEN_SECRET_KEY=your_very_secure_secret_key_here
COOKIE_DOMAIN=localhost

# SMTP
SMTP_PORT=587
SMTP_USERNAME=admin
SMTP_PASSWORD=admin

# Настройки Redis
REDIS_PORT=6379
REDIS_PASSWORD=default

# Настройки базы данных
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=gidrator_db

# RabbitMQ
RABBITMQ_USER=guest
RABBITMQ_PASS=guest
RABBITMQ_PORT=5672
RABBITMQ_HOST=localhost
RABBITMQ_EXCHANGE=gidrator

# Настройки CORS
ALLOW_ORIGINS=["*"]
ALLOW_CREDENTIALS=true
ALLOW_METHODS=["*"]
ALLOW_HEADERS=["*"]
```

> [!IMPORTANT]
> - Никогда не коммитьте файлы .env.dev или другие файлы с реальными учетными данными в репозиторий!
> - Убедитесь, что они добавлены в .gitignore.
> - Обязательно замените `TOKEN_SECRET_KEY` на уникальный секретный ключ!

## Первый запуск

```bash
uv run activate
```

## Последующий запуск

Для активации виртуального окружения без запуска режима разработки
(например, нужно сделать миграции в соседнем терминале при запущенной инфраструктуре):

```bash
uv run setup
```

Запуск в режиме разработки (с hot-reload) без инфраструктуры (базы данных и т.д.)
```bash
uv run dev
```

Или запуск в режиме разработки (с hot-reload) с инфраструктурой одной командой:

```bash
uv run activate
```

## Разработка

### Процесс разработки такой:
- Разработка идёт от `development`
- В `development` мерджим фичи
- Тестим на `development`
- Когда всё ок - мерджим `development` в main

Если вы хотите внести изменения или улучшения, пожалуйста, следуйте этим шагам:

1. Переключаемся на `development` и подтягиваем последние изменения с удалённого репозитория:
```bash
git checkout development
git pull origin development
```

2. От `development` создаем свою ветку разработки и сразу на неё переключаемся:
```bash
git checkout -b feature/your-name-of-feature
```

3. Кодим и по итогу добавляем все изменения в индекс:
```bash
git add .
```

4. Создаём коммит с описанием изменений
```bash
git commit -m "feat: your-changes"
```

5. Перед пушем обновляем ветку от `development`, то есть
 1) Переключаемся обратно на development
 2) Подтягиваем новые изменения
 3) Возвращаемся на свою ветку
 4) Переносим свои изменения поверх последней версии `development`

```bash
git checkout development
git pull origin development
git checkout feature/your-name-of-feature
git rebase development
```

6. Отправляем свою ветку в удалённый репозиторий:
```bash
git push origin feature/your-name-of-feature --force-with-lease
```

7. Создаем Pull Request в dev ветку!
> 1) Жмём кнопку "New Pull Request"
> 2) В base выбираем `development` (КУДА льём)
> 3) В compare выбираем свою ветку feature/your-name-of-feature (ОТКУДА льём)
> 4) Пишешь нормальное описание что сделали
> 5) Добавляем ревьюеров
> 6) Создаёи PR

Либо просто делаем merge в development ветку из своей feature/your-name-of-feature ветки.
```bash
git checkout development
git merge feature/your-name-of-feature
```

8. После тестирования на `development`, создаём PR из `development` в `main`.
> 1) Создаём новый PR
> 2) В base выбираем main (КУДА льём)
> 3) В compare выбираем development (ОТКУДА льём)
> 4) Описываем все изменения которые войдут в прод
> 6) Ждём подтверждения от тимлида

Либо просто делаем merge в main ветку из development ветки.
```bash
git checkout main
git merge development
```

9. Удаляем свою ветку feature/your-name-of-feature

Локально:

```bash
git branch -d feature/your-name-of-feature
```
Удалённо:
```bash
git push origin --delete feature/your-name-of-feature
```
