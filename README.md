### Тестовое задание
*Стек: python:3.10, Postgres:12.4*
####

### Для проверки задания:
`Требования:`  
* [обязательно] установленная платформа [Docker](https://docs.docker.com/get-docker/)
* [обязательно] наличие Google-аккаунта.

---
1. Создать сервисный аккаунт [Google](https://developers.google.com/identity/protocols/oauth2/service-account?hl=ru).
2. Ключ, полученный в результате регистрации сервисного аккаунта, сохранить как *token.json* в директории [secrets](./secrets).
3. При необходимости, в список [EMAIL_ADDRESSES](./config/settings.py) добавить email пользователя, которому следует открыть доступ к облаку.
4. При необходимости, изменить параметры подключения к базе данных в файле [secrets/db.json](./secrets/db.json).
5. Создать и запустить образ с PostgreSQL с учетом изменений в файле [secrets/db.json](./secrets/db.json).

```python
docker run --name psql -e POSTGRES_DB=postgres -e  POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:12.4-alpine
```
6. Установить зависимости
```python
pip install poetry
poetry install
```

7. Запустить скрипт
```python
python run.py
```
