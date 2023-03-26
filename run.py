import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from services.gsheets import GSheets
from services.cbr import CBR
from services.db import DB
from config.settings import GS_POLLING_INTERVAL, CBR_POLLING_INTERVAL, ROWS_SHIFT

if __name__ == '__main__':
    scheduler = AsyncIOScheduler()
    sheet = GSheets()
    cbr = CBR()
    with DB() as db:
        db.update_price_rub(cbr.currency_rate)
        print('Курс доллара США:', cbr.currency_rate, '\n')


    async def sheet_check_job():
        print('[sheet_check_job] проверка GSheet-таблицы на наличие изменений')
        if not sheet.check_changes():
            print('[sheet_check_job] изменений нет')
            return

        with DB() as db_:
            print('[sheet_check_job] обновление значений в базе')
            rows = sheet.get_rows()
            for index, row in enumerate(rows):
                if len(row) < 4:
                    continue
                row.extend((0, index+ROWS_SHIFT+1))

            db_.update(rows)
            print('[sheet_check_job] выполнено!')

    async def currency_rate_check_job():
        with DB() as db_:
            db_.update_cost_rub(cbr.fetch_currency_rate())
            print('[currency_rate_check_job] курс USD/RUB успешно обновлен:', cbr.currency_rate)

    scheduler.add_job(currency_rate_check_job, 'interval', hours=CBR_POLLING_INTERVAL)
    scheduler.add_job(sheet_check_job, 'interval', minutes=GS_POLLING_INTERVAL)
    scheduler.start()

    print('Press Ctrl+C to exit\n')

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        asyncio.get_event_loop().stop()
