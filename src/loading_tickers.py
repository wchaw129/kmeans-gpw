import pandas as pd
import requests
from typing import Optional
from datetime import datetime
from io import StringIO
from src.config import DATA_DIR
from pathlib import Path

def load_tickers_from_website(
        url: str = "https://www.bankier.pl/inwestowanie/profile/quote.html?symbol=WIG",
        save_to_file: bool = False,
        file_name: str = None
) -> pd.DataFrame | None:
    
    """
    Pobiera listę spółek z tabeli na stronie Bankier.pl.
    """

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'} 

          
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() 
        tables = pd.read_html(StringIO(response.text), decimal=',', thousands=' ')

        if len(tables) > 0:
            df = tables[0]
            print("Pobrano pomyślnie")
            if save_to_file:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                df.to_csv(f'data/{file_name if file_name else f"tickers_{timestamp}"}.csv')
            return df
        else:
            print("Nie znaleziono żadnej tabeli na stronie.")
            return None

    except Exception as e:
        print(f"Wystąpił błąd: {e}")
        return None


def load_tickers_from_file(
        filepath: Path | str = DATA_DIR / 'WIG_ticker_list.csv', 
        sep: str = ';'
) -> pd.DataFrame | None:
    """
    Ładuje tabelę z pliku CSV.
    Kolumna Ticker powinna zawierać tickery spółek w tabeli
    """

    try:
        df = pd.read_csv(filepath, sep = sep)
        print('Pobrano pomyślnie')
        return df
    
    except FileNotFoundError:
        print('Nie znaleziono pliku')
        return None
    
    except Exception as e:
        print(f"Wystąpił błąd: {e}")
        return None        
    
