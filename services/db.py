import psycopg2

from config.settings import (DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, TABLE_NAME,
                             TABLE_FIELDS_INDEX, TABLE_FIELDS_TYPE, TABLE_FIELDS_ORDER
                             )


def _prepare_query(row: list, fields_order: tuple) -> str:
    result = '('
    last_field: str = fields_order[-1]
    for field in fields_order:
        result += '\'' if field == 'delivery_date' else ''
        result += str(row[TABLE_FIELDS_INDEX[field]])
        result += '\'' if field == 'delivery_date' else ''
        result += TABLE_FIELDS_TYPE[field]
        result += ', ' if field != last_field else ''

    return result + ')'


class DB:

    def __init__(self):
        self.connected = False
        self.connect = None
        self.cursor = None

    def __enter__(self):
        self._connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close()

    def _connect(self):
        self.connected = True
        self.connect = psycopg2.connect(
            dbname=DB_NAME[0],
            user=DB_USER[0],
            password=DB_PASSWORD[0],
            host=DB_HOST[0]
        )
        self.cursor = self.connect.cursor()
        self.connect.autocommit = True

        #: Проверка наличия таблицы в базе
        self._query_execute('''
            SELECT relname
            FROM pg_class
            WHERE relkind='r' AND relname !~ '^(pg_|sql_)';
            ''')
        tables = map(lambda x: x[0], self.cursor.fetchall())
        if not TABLE_NAME.lower() in tables:
            print(f'DB: таблица "{TABLE_NAME}" не обнаружена в базе данных {DB_NAME[0]}!')
            print('DB: создание таблицы...')

            #: Создаем таблицу
            query = f'''
            CREATE TABLE {TABLE_NAME} (
            id                          SERIAL              NOT NULL PRIMARY KEY,
            {TABLE_FIELDS_ORDER[0]}     INTEGER             NOT NULL UNIQUE,
            {TABLE_FIELDS_ORDER[1]}     INTEGER             NOT NULL,
            {TABLE_FIELDS_ORDER[2]}     INTEGER             NOT NULL UNIQUE,
            {TABLE_FIELDS_ORDER[3]}     NUMERIC(12, 2)      NOT NULL,
            {TABLE_FIELDS_ORDER[4]}     NUMERIC(12, 2)      NOT NULL,
            {TABLE_FIELDS_ORDER[5]}     CHAR(10)            NOT NULL
            );
            '''
            try:
                self._query_execute(query)
                print(f'DB: таблица "{TABLE_NAME}" успешно создана в базе данных {DB_NAME[0]}.')
            except Exception as error:
                print(f'DB: create table error. {error}')
                self._close()

            #: Добавляем функцию
            query = f'''
            CREATE
            OR REPLACE FUNCTION update_orders(
            arg_{TABLE_FIELDS_ORDER[0]} INTEGER,
            arg_{TABLE_FIELDS_ORDER[1]} INTEGER,
            arg_{TABLE_FIELDS_ORDER[2]} INTEGER,
            arg_{TABLE_FIELDS_ORDER[3]} DOUBLE PRECISION,
            arg_{TABLE_FIELDS_ORDER[4]} DOUBLE PRECISION,
            arg_{TABLE_FIELDS_ORDER[5]} CHAR(10)
            )
            RETURNS VOID AS
            $$
            DECLARE
            BEGIN
            UPDATE {TABLE_NAME} as o SET
            {TABLE_FIELDS_ORDER[1]} = arg_{TABLE_FIELDS_ORDER[1]},
            {TABLE_FIELDS_ORDER[2]} = arg_{TABLE_FIELDS_ORDER[2]},
            {TABLE_FIELDS_ORDER[3]} = arg_{TABLE_FIELDS_ORDER[3]},
            {TABLE_FIELDS_ORDER[4]} = arg_{TABLE_FIELDS_ORDER[4]},
            {TABLE_FIELDS_ORDER[5]} = arg_{TABLE_FIELDS_ORDER[5]}
            WHERE {TABLE_FIELDS_ORDER[0]} = arg_{TABLE_FIELDS_ORDER[0]};
            IF NOT FOUND THEN
                INSERT INTO {TABLE_NAME}({TABLE_FIELDS_ORDER[0]}, {TABLE_FIELDS_ORDER[1]}, {TABLE_FIELDS_ORDER[2]}, {TABLE_FIELDS_ORDER[3]}, {TABLE_FIELDS_ORDER[4]}, {TABLE_FIELDS_ORDER[5]})
                VALUES (arg_{TABLE_FIELDS_ORDER[0]}, arg_{TABLE_FIELDS_ORDER[1]}, arg_{TABLE_FIELDS_ORDER[2]}, arg_{TABLE_FIELDS_ORDER[3]}, arg_{TABLE_FIELDS_ORDER[4]}, arg_{TABLE_FIELDS_ORDER[5]});
            END IF;
            END;
            $$
            LANGUAGE plpgsql;
            '''
            try:
                self._query_execute(query)
                print(f'DB: функция "update_orders" успешно создана в базе данных {DB_NAME[0]}.')
            except Exception as error:
                print(f'DB: create function error. {error}')
                self._close()

    def _close(self) -> None:
        self.connected = False
        self.cursor.close()
        self.connect.close()
        self.connect = None
        self.cursor = None

    def _query_execute(self, query: str) -> None:
        try:
            self.cursor.execute(query)
        except Exception as error:
            print('DB: PostgreSQL execution error:', error)

    def connect(self) -> None:
        """
        Производит подключение к базе данных
        :return:
        """
        self._connect()

    def update(self, rows: list[list]) -> None:

        if not self.connected:
            self._connect()

        query = ''
        for row in rows:
            query += f'SELECT update_orders{_prepare_query(row, TABLE_FIELDS_ORDER)};\n'
        self._query_execute(query)

    def close(self) -> None:
        self._close()

    def update_price_rub(self, price: float) -> None:
        """
        Обновляет цену в рублях по текущему курсу USD
        :param price: курс USD
        :return: None
        """
        if not self.connected:
            self._connect()

        query = f'''
        UPDATE {TABLE_NAME}
        SET price_rub = price_usd * {price};
        '''

        self._query_execute(query)
