# BloodSite (Backend Starter)

## Быстрый старт (Windows / macOS / Linux)

1) Установите Python 3.11+ и pip.
2) Создайте и активируйте виртуальное окружение:
   - Windows (PowerShell):
     ```ps1
     py -3.11 -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - Linux/macOS:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
3) Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4) (Опционально) Скопируйте `.env.example` в `.env` и отредактируйте.
   По умолчанию используется SQLite. Для PostgreSQL заполните переменные:
   `POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT`.
5) Примените миграции и загрузите демо-данные:
   ```bash
   python manage.py migrate
   python manage.py loaddata fixtures/core/siteconfig.json \
                      fixtures/core/menuitem.json \
                      fixtures/core/heroblock.json \
                      fixtures/core/article.json \
                      fixtures/core/contactchannel.json \
                      fixtures/core/bloodcenter.json
   ```
6) Создайте администратора и запустите сервер:
   ```bash
   python manage.py createsuperuser
   python manage.py runserver
   ```

Откройте:
- Swagger: http://127.0.0.1:8000/api/docs/
- API:
  - GET /api/v1/health/
  - GET /api/v1/site/config/
  - GET /api/v1/site/menu/
  - GET /api/v1/site/hero/
  - GET /api/v1/articles/?category=news&q=...
  - GET /api/v1/articles/<slug>/
  - GET /api/v1/centers/?city=Almaty
  - GET /api/v1/contacts/

> `GET /api/v1/bonuses/me/` требует авторизацию (в проекте подключена стандартная Django аутентификация; JWT добавим позже).

## Переключение на PostgreSQL
1) Установите PostgreSQL и создайте БД/пользователя.
2) В `.env` задайте переменные, например:
   ```env
   POSTGRES_DB=bloodsite
   POSTGRES_USER=blooduser
   POSTGRES_PASSWORD=strongpass
   POSTGRES_HOST=127.0.0.1
   POSTGRES_PORT=5432
   ```
3) Примените миграции заново на новой БД:
   ```bash
   python manage.py migrate
   ```

## Дальше
- Добавим JWT (djangorestframework-simplejwt) и эндпоинты /auth/* или интеграцию с внешним окном коллег (OIDC/SAML).
- Расширим модели/фильтры (геопоиск центров, пагинация новостей).
- Включим кэширование Redis и настройки безопасности для продакшна.
