import httpx
import xml.etree.ElementTree as ET


class CurrencyRate:

    def __init__(self) -> None:
        self.currency_rate = {}

        response = httpx.get('https://www.cbr.ru/scripts/XML_daily.asp')
        if response.status_code != 200:
            raise Exception('Не удаётся получить курсы валют от ЦБРФ')

        root = ET.fromstring(response.content)
        for child in root.findall('Valute'):
            nominal = int(child.find('Nominal').text)
            code = child.find('CharCode').text
            value = float(child.find('Value').text.replace(',', '.'))

            self.currency_rate[code] = value / nominal

    def conv_to_rur(self, value: float | int, currency: str) -> float:
        return float(value) * self.currency_rate[currency.upper()]
