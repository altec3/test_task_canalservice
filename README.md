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
3. При необходимости, в список [EMAIL_ADDRESSES](./config/settings.py) добавить email пользователей, которым следует открыть доступ к облаку.
4. Рядом с файлом *docker-compose.yaml* положить файл *.env* с параметрами для подключения к базе данных (см. файл [.env.example](.env.example)):
5. Установить зависимости
```python
pip install poetry
poetry install
```
6. Собрать и запустить контейнеры со скриптом и базой данных (БД).

```python
docker-compose up --build -d
```
В результате будет собран и запущен контейнер с работающим скриптом, а так же скачан и запущен контейнер с БД PostgreSQL.  
Посмотреть список запущенных контейнеров можно командой:
```python
docker-compose ps
```
Посмотреть статус работы скрипта:
```python
docker-compose logs script
```
