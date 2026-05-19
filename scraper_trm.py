import requests
from datetime import datetime
import json

def fetch_daily_trm() -> dict[str, float | str | None]:
    """
    Fetches the daily TRM (Exchange Rate) from the Superintendencia Financiera API,
    cleans the data, and returns a structured dictionary.

    Returns:
        dict: A dictionary containing the TRM value and date, or None if the
              request fails.
    """
    
    url = 'https://www.superfinanciera.gov.co/loader.php?lServicio=Bloques&lTipo=webData&lFuncion=showTrmDate'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    res = requests.get(url, headers=headers)

    if res.status_code == 200:
        raw_data = res.json()

        internal_data = json.loads(raw_data['informacion'])

        trm_value = float(internal_data["valor"].strip().replace(',', ''))
        trm_range = internal_data["fecha"].strip()

        trm_raw_date = trm_range[-10:]
        object_date = datetime.strptime(trm_raw_date, '%d-%m-%Y')
        trm_date = object_date.strftime('%Y-%m-%d')

        return {
            'trm_value': trm_value,
            'trm_date': trm_date
        }
    else:
        print(f"Failed to connect to the API. Status code: {res.status_code}")
        return None

if __name__ == "__main__":
    result = fetch_daily_trm()
    print("Local scraper test result:", result)