### Тестовое задание
*Стек: python:3.10, Postgres:12.4*  
*Среда разработки: PyCharm*

---
### Описание задания

Скрипт выполняет следующие функции:
1. При помощи Google API получает данные с документа, сделанного в [Google Sheets](https://docs.google.com/spreadsheets/d/1f-qZEX1k_3nj5cahOzntYAnvO4ignbyesVO7yuBdv_g/edit).
2. Полученные данные добавляются в БД с добавлением колонки «стоимость в руб.» Данные для перевода $ в рубли берутся по курсу [ЦБ РФ](https://www.cbr.ru/development/SXML/).
3. Скрипт работает постоянно для обеспечения обновления данных в онлайн режиме.  

Решение упаковано в docker контейнер.

---

### Для проверки задания:
`Требования:`  
* [обязательно] установленная платформа [Docker](https://docs.docker.com/get-docker/)
* [обязательно] наличие Google-аккаунта.

---
1. Создать сервисный аккаунт [Google](https://developers.google.com/identity/protocols/oauth2/service-account?hl=ru).
2. Ключ, полученный в результате регистрации сервисного аккаунта, сохранить как *token.json* в директории [./secrets](./secrets).
3. При необходимости, в список [EMAIL_ADDRESSES](./config/settings.py) добавить email пользователей, которым следует открыть доступ к облаку.
4. Рядом с файлом *docker-compose.yaml* положить файл *.env* с параметрами для подключения к базе данных (см. файл [.env.example](.env.example)):
5. Собрать и запустить контейнеры со скриптом и базой данных (БД):
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
Остановить контейнеры:
```python
docker-compose down
```
#### Для просмотра изменений в БД (IDE PyCharm)
1. [Настроить](https://www.jetbrains.com/help/pycharm/postgresql.html) подключение к базе.
2. Открыть необходимую таблицу базы для просмотра: *View -> Tool Windows -> Database*.

#### Ручной запуск
1. Выполнить пункты 1 - 4 выше
2. Создать виртуальное окружение:
```python
python -m venv venv
./venv/Scripts/Activate.ps1 # Windows PowerShell
venv\Scripts\activate.bat   # Windows CMD
source venv/bin/activate    # Linux, MacOS
```
3. Установить зависимости:
```python
pip install poetry
poetry install
```
4. Запустить образ с PostgreSQL с учетом параметров в .env-файле:
```python
docker run --name psql -e POSTGRES_DB=postgres -e  POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:12.4-alpine
```
где:  
POSTGRES_DB - имя БД (DB_NAME),  
POSTGRES_PASSWORD - пароль для доступа к БД (DB_PASSWORD).  
5. Запустить скрипт:
```python
python run.py
```
