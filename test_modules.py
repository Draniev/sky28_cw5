from currency_rate import CurrencyRate

cur = CurrencyRate()

print(f'100 USD = {cur.convert_to_rur(100, "USD")}')
