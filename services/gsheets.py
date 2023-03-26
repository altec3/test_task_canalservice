import json
import os
from datetime import datetime

from config.settings import (SOURCE_SPREADSHEET_ID,
                             EMAIL_ADDRESSES, STATE_FILE,
                             NEW_SHEET_NAME, CONFIG_DIR, ROWS_SHIFT,
                             )
from services.api_client import GoogleApiService

STATE_FILE_PATH = CONFIG_DIR.joinpath(STATE_FILE)


class GSheets:

    def __init__(self):
        service = GoogleApiService()
        self.sheets_service = service.get_sheets_service()
        self.drive_service = service.get_drive_service()
        self.source_spreadsheet_id = SOURCE_SPREADSHEET_ID

        #: Загрузка последнего сохраненного состояния
        if not STATE_FILE_PATH.exists():
            self.last_update = f'{datetime.now():%X %d.%m.%Y}'
            self._create()

        with open(STATE_FILE_PATH, 'r') as state_file:
            state: dict = json.load(state_file)

        self.spreadsheet_id = state.get('spreadsheet_id')
        self.sheet_id = state.get('sheet_id')
        self.start_page_token = state.get('start_page_token')
        self.page_token = state.get('start_page_token')
        self.last_update = state.get('last_update')

        if not self.spreadsheet_id or not self.start_page_token or not self.last_update:
            print(f'GSheets error: {STATE_FILE} has wrong structure. A new spreadsheet will be created')
            self._create()

    def _create(self) -> None:

        #: Создаем новую таблицу
        request = self.sheets_service.spreadsheets().create(body={
            'properties': {
                'title': 'New spreadsheet',
                'locale': 'ru_RU',
            }
        })
        response: dict = request.execute()

        self.spreadsheet_id = response.get('spreadsheetId')
        print(f'GSheets: Новая таблица успешно создана.\nURL: {response.get("spreadsheetUrl")}')

        #: Получим начальную страницу для отслеживания изменений файла
        request = self.drive_service.changes().getStartPageToken()
        response: dict = request.execute()
        self.start_page_token = response.get("startPageToken")
        self.page_token = response.get("startPageToken")

        #: Назначим права на доступ к созданной таблице
        for email in EMAIL_ADDRESSES:
            self.drive_service.permissions().create(
                fileId=self.spreadsheet_id,
                body={
                    'type': 'user',
                    'role': 'writer',
                    'emailAddress': email,
                },
                fields='id'
            ).execute()

        #: Скопируем в созданную таблицу лист из таблицы-источника
        response: dict = self._copy()
        self.sheet_id = response.get('sheetId')
        #: Переименуем лист, на который произведено копирование
        self._rename_sheet(self.sheet_id, NEW_SHEET_NAME)
        print(f'Данные из таблицы-источника успешно скопированы на лист "{NEW_SHEET_NAME}".\n')
        #: Сохраним начальное состояние таблицы
        self._save_state()

    def _copy(self):

        response = self.sheets_service.spreadsheets().sheets().copyTo(
            spreadsheetId=self.source_spreadsheet_id,
            sheetId=0,
            body={'destination_spreadsheet_id': self.spreadsheet_id}
        )
        return response.execute()

    def _rename_sheet(self, sheet_id: str, new_name: str):

        response = self.sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body={'requests': {
                'updateSheetProperties': {
                    'properties': {
                        'sheetId': sheet_id,
                        'title': new_name,
                    },
                    'fields': 'title',
                }
            }}
        )

        return response.execute()

    def check_changes(self) -> bool:
        """
        Проверяет наличие изменений в таблице
        :return: bool
        """

        is_changed: bool = False
        self.page_token: str = self.start_page_token
        start_page_token: str = self.start_page_token

        try:
            while self.page_token is not None:

                request = self.drive_service.changes().list(
                    pageToken=self.page_token,
                    spaces='drive',
                )
                response: dict = request.execute()

                for change in response.get('changes'):
                    file_id = change.get("fileId")
                    if file_id == self.spreadsheet_id:
                        is_changed = True
                if 'newStartPageToken' in response:
                    self.start_page_token = response.get('newStartPageToken')

                self.page_token = response.get('nextPageToken')

            if start_page_token != self.start_page_token:
                self.last_update = f'{datetime.now():%X %d.%m.%Y}'
                self._save_state()  #: сохраним статус поиска изменений

        except Exception as error:
            print(f'GSheets error: unable to fetch {self.spreadsheet_id} table with Google Sheets API:', error)
        finally:
            return is_changed

    def _save_state(self) -> None:

        with open(os.path.join(CONFIG_DIR, STATE_FILE), 'w') as state_file:
            json.dump({
                'spreadsheet_id': self.spreadsheet_id,
                'sheet_id': self.sheet_id,
                'start_page_token': self.start_page_token,
                'last_update': self.last_update,
            }, state_file, indent=4)

    def get_rows(self) -> list[list]:
        """
        Получает табличные данные
        :Note: По-хорошему следует получать данные частями
        :return: list
        """

        request = self.sheets_service.spreadsheets().values().batchGet(
            spreadsheetId=self.spreadsheet_id,
            ranges=[NEW_SHEET_NAME]
        )
        response: dict = request.execute()

        value_ranges: list = response.get('valueRanges')
        for value_range in value_ranges:
            values: list[list] = value_range.get('values', [])

            return values[ROWS_SHIFT:]
