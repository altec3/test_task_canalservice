import httplib2
from locale import atof
from datetime import datetime
import xml.etree.ElementTree as et

from config.settings import VALUTE_CHAR_CODE


class CBR:

    def __init__(self):
        self.client = httplib2.Http()
        self.currency_rate = 0
        self.fetch_currency_rate()

    def fetch_currency_rate(self):

        try:
            cbr_response, cbr_response_s = self.client.request(
                f'http://www.cbr.ru/scripts/XML_daily.asp?date_req={datetime.now().strftime("%d/%m/%Y")}', 'GET',
            )

            if cbr_response.get('status') != '200':
                print('Error fetching currency from http://www.cbr.ru/ :\n\t', cbr_response_s)

            try:
                currencies = et.fromstring(cbr_response_s)

                for currency in currencies:
                    attribs = {attrib.tag: attrib.text for attrib in currency}
                    if VALUTE_CHAR_CODE not in attribs.values():
                        continue
                    self.currency_rate = atof(attribs['Value'].replace(',', '.'))

            except ValueError:
                print(f'Error: unable to fetch {VALUTE_CHAR_CODE} currency rate. The CBR API has changed')

        except Exception as error:
            print(f'Error: unable to fetch {VALUTE_CHAR_CODE} currency rate:', error)
        finally:
            return self.currency_rate
