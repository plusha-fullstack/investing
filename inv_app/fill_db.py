import requests
from django.conf import settings
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loginSignup.settings')
django.setup()

from base.models import Crypto,Stock,Bond,Fund

api_key = '0a3a6748-7ae9-4641-8889-ac69efb1d92c'
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

parameters = {
    'start': '1',
    'limit': '1000',
    'convert': 'USD'
}

headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': api_key,
}

response = requests.get(url, headers=headers, params=parameters)
data = response.json()['data']

for crypto in data:
    if crypto['quote']['USD']['market_cap'] >= 1000000 and crypto['quote']['USD']['volume_24h'] >= 10000 and crypto['cmc_rank'] <= 1000:
        crypto_data = {
            'id': crypto['id'],
            'name': crypto['name'],
            'symbol': crypto['symbol'],
            'price': crypto['quote']['USD']['price'],
            'volume_24h': crypto['quote']['USD']['volume_24h'],
            'market_cap': crypto['quote']['USD']['market_cap']
        }

        crypto_instance = Crypto(**crypto_data)
        crypto_instance.save()

def fetch_stock_data():
    url = "https://iss.moex.com/iss/engines/stock/markets/shares/boards/tqbr/securities.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


def fetch_bonds_data():
    url = "https://iss.moex.com/iss/engines/stock/markets/bonds/securities.json"  # Replace with the correct URL for bonds
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()
def fetch_funds_data():
    url = "https://iss.moex.com/iss/engines/stock/markets/index/securities.json"  # Replace with the correct URL for bonds
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


#stock
def parse_moex_data(data):
    securities_columns = data['securities']['columns']
    securities_data = data['securities']['data']
    market_columns = data['marketdata']['columns']
    market_data = data['marketdata']['data']
    
    return securities_columns, securities_data, market_columns, market_data


def save_stocks_to_db(securities_columns, securities_data):
    secid_index = securities_columns.index('SECID')
    shortname_index = securities_columns.index('SHORTNAME')
    # Add other indices as needed

    for sec in securities_data:
        stock_instance = Stock(
            ticker=sec[secid_index], 
            name=sec[shortname_index],
            price=0,
            volume_24h=0, 
            market_cap=0
        )
        stock_instance.save()

def update_stocks_data_in_db(market_columns, market_data):
    secid_index = market_columns.index('SECID')
    last_index = market_columns.index('LAST')
    valtoday_index = market_columns.index('VALTODAY')
    issuecapitalization_index = market_columns.index('ISSUECAPITALIZATION')

    for data in market_data:
        ticker = data[secid_index]
        try:
            stock_instance = Stock.objects.get(ticker=ticker)
            stock_instance.price = data[last_index] if data[last_index] is not None else 0  # LAST from marketdata
            stock_instance.volume_24h = data[valtoday_index] if data[valtoday_index] is not None else 0  # VOLTODAY from marketdata
            stock_instance.market_cap = data[issuecapitalization_index] if data[issuecapitalization_index] is not None else 0  # ISSUECAPITALIZATION from marketdata
            stock_instance.save()
        except Stock.DoesNotExist:
            print(f"Stock with ticker {ticker} does not exist in the database.")
        except IndexError:
            print(f"Index error for {ticker} in market data.")
        except Exception as e:
            print(f"Error updating stock {ticker}: {e}")


moex_data = fetch_stock_data()
securities_columns, securities_data, market_columns, market_data = parse_moex_data(moex_data)
save_stocks_to_db(securities_columns, securities_data)
update_stocks_data_in_db(market_columns, market_data)

#bonds

def save_bonds_to_db(securities_columns, securities_data):
    secid_index = securities_columns.index('SECID')
    shortname_index = securities_columns.index('SHORTNAME')
    issue_size = securities_columns.index('ISSUESIZE')

    for sec in securities_data:
        bond_instance = Bond(
            ticker=sec[secid_index],
            name=sec[shortname_index],
            price=0,
            volume_24h=0,
            issue_size=sec[issue_size]
        )
        bond_instance.save()

def update_bond_data_in_db(market_columns, market_data):
    secid_index = market_columns.index('SECID')
    last_index = market_columns.index('LAST')
    valtoday_index = market_columns.index('VALTODAY')

    for data in market_data:
        ticker = data[secid_index]  
        try:
            bond_instance = Bond.objects.get(ticker=ticker)
            last_price = data[last_index] if data[last_index] is not None else 0
            if last_price == 0:
                bond_instance.delete()
                print(f"Bond with ticker {ticker} has a null or zero price and was deleted.")
            else:
                bond_instance.price = last_price  # LAST from marketdata
                bond_instance.volume_24h = data[valtoday_index] if data[valtoday_index] is not None else 0  # VALTODAY from marketdata
                bond_instance.save()
        except Bond.DoesNotExist:
            print(f"Bond with ticker {ticker} does not exist in the database.")
        except IndexError:
            print(f"Index error for {ticker} in market data.")
        except Exception as e:
            print(f"Error updating bond {ticker}: {e}")

moex_data = fetch_bonds_data()
securities_columns, securities_data, market_columns, market_data = parse_moex_data(moex_data)
save_bonds_to_db(securities_columns, securities_data)
update_bond_data_in_db(market_columns, market_data)


def save_funds_to_db(securities_columns, securities_data):
    secid_index = securities_columns.index('SECID')
    shortname_index = securities_columns.index('SHORTNAME')

    for sec in securities_data:
        fund_instance = Fund(
            ticker=sec[secid_index],  
            name=sec[shortname_index],
            price=0, 
            volume_24h=0, 
            market_cap=0
        )
        fund_instance.save()

def update_fund_data_in_db(market_columns, market_data):
    secid_index = market_columns.index('SECID')
    current_index = market_columns.index('CURRENTVALUE')
    valtoday_index = market_columns.index('VALTODAY')
    capitalization_index = market_columns.index('CAPITALIZATION')

    for data in market_data:
        ticker = data[secid_index]
        try:
            fund_instance = Fund.objects.get(ticker=ticker)
            fund_instance.price = data[current_index] if data[current_index] is not None else 0  # LAST from marketdata
            fund_instance.volume_24h = data[valtoday_index] if data[valtoday_index] is not None else 0  # VOLTODAY from marketdata
            fund_instance.market_cap = data[capitalization_index] if data[capitalization_index] is not None else 0  # ISSUECAPITALIZATION from marketdata
            fund_instance.save()
        except Fund.DoesNotExist:
            print(f"Fund with ticker {ticker} does not exist in the database.")
        except IndexError:
            print(f"Index error for {ticker} in market data.")
        except Exception as e:
            print(f"Error updating fund {ticker}: {e}")


moex_data = fetch_funds_data()
securities_columns, securities_data, market_columns, market_data = parse_moex_data(moex_data)
save_funds_to_db(securities_columns, securities_data)
update_fund_data_in_db(market_columns, market_data)
