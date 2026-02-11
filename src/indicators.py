import pandas as pd
from io import StringIO
import requests 
import time

def CountIndicators(
        company_name: str,
        ticker: str,
        mean_periods: int
) -> dict | None:
    
    dict = {}

    DIR = rf'../data/raporty/{company_name}.csv' 
    try:
        df = pd.read_csv(DIR, sep = ',')
        df = df.set_index('Dane / Okres').iloc[:, 2:]
        df.columns = df.columns.str.slice(-4).astype(int)
    except Exception as e:
        print(e)
        return None

#ROE
    zysk = df.loc["Zysk netto", :]
    if isinstance(zysk, pd.Series):
        pass
    else: 
        zysk = zysk.iloc[0, :]
    
    zysk = pd.to_numeric(zysk.str.replace(' ', '')) #zysk netto
    kw = pd.to_numeric(df.loc['Kapitał własny', :].str.replace(" ", '')) #kapital wlasny

    ROE_py = zysk/kw #ROE per year
    dict['ROE'] = ROE_py[mean_periods:].mean()

#ROA 
    if 'Aktywa trwałe' in df.index:
        aktywa = pd.to_numeric(df.loc['Aktywa trwałe', :].str.replace(" ", ''))
    else: 
        aktywa = pd.to_numeric(df.loc['Rzeczowe aktywa trwałe', :].str.replace(" ", ''))

    ROA_py = zysk/aktywa
    dict['ROA'] = ROA_py[mean_periods:].mean()

#CAGR przychodów
    #przychody = pd.to_numeric(df.loc['Przychody', :].str.replace(" ", ''))
    #CAGR = (przychody.iloc[-1] / przychody.iloc[-mean_periods]) ** (1/mean_periods) - 1
    #dict['CAGR'] = CAGR

#stopa dywidendy
    liczba_akcji = pd.to_numeric(df.loc['Liczba akcji', :].str.replace(" ", ''))
    dyw = pd.to_numeric(df.loc['Dywidenda', :].str.replace(" ", '')) * -1000 #kwota przeznaczona na dywidende w danym roku
    DPS = dyw/liczba_akcji #dywidenda na akcje
    DPS.name = 'DPS'

    share_prices = get_share_price(ticker)
    PPS = share_prices.groupby('rok')['Zamkniecie'].mean() #cena za akcje
    DY_table = pd.merge(DPS, PPS, how = 'inner', left_index = True, right_index = True)
    DY_table['DY'] = DY_table['DPS'] / DY_table['Zamkniecie']
    dict['DY'] = DY_table['DY'][-mean_periods:].mean()
    
#dynamika EPS 
    EPS = zysk*1000/liczba_akcji
    dict['dynamika EPS'] = EPS.pct_change()[-mean_periods:].mean()

#P/E
    PE = PPS[PPS.index <= 2024] / EPS
    dict['P/E'] = PE[-mean_periods:].mean()
    
#P/BV
    PBV = PPS[PPS.index <= 2024] / (kw*1000/liczba_akcji)
    dict['P/BV'] = PBV[-mean_periods:].mean()
    
# std stop zwrotu
    price = share_prices[share_prices['rok'] == 2024]
    dict['std'] = price['Zamkniecie'].pct_change().std()

#wsp beta
# TODO

    return dict


def get_share_price(
        ticker: str,
) -> pd.DataFrame | None:
    
    url = rf'https://stooq.pl/q/d/l/?s={ticker}&i=d'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'} 
    try:
        r = requests.get(url, headers = headers, timeout = 60)
        if r.status_code == 200:
            table = StringIO(r.text)
            df = pd.read_csv(table, index_col = 'Data', parse_dates = True)
            df['rok'] = df.index.year
            time.sleep(1)
            return df
        else:
            print('error')
            return None
    except Exception as e:
        print(e)
        return None
    

