import pandas as pd
from io import StringIO
import requests 
import time
from src.processing import read_file, clean_series


def get_income(
        company_name: str,
        #year: int
) -> pd.Series | None: 
    
    df = read_file(company_name)
    zysk = df.loc["Zysk netto", :]
    zysk = df.loc["Zysk netto", :]
    if isinstance(zysk, pd.Series):
        pass
    else: 
        zysk = zysk.iloc[0, :]
    return clean_series(zysk)


def aagr(
        series: pd.Series
) -> pd.Series:
    return series.diff() / series.shift(1).abs()

def CountIndicators(
        company_name: str,
        ticker: str,
        mean_periods: int,
        cagr_period: int
) -> dict | None:
    
    dict = {}

    df = read_file(company_name)

#dynamika ROE
    profit = get_income(company_name) #zysk netto
    equity_capital = clean_series(df.loc['Kapitał własny', :]) #kapital wlasny
    ROE_py = profit/equity_capital #ROE per year
    ROE_aagr = aagr(ROE_py)
    dict['ROE'] = ROE_aagr[mean_periods:].mean()

#dynamika ROA 
    if 'Suma bilansowa' in df.index:
        aktywa = pd.to_numeric(df.loc['Suma bilansowa', :].str.replace(" ", ''))
    else: 
        aktywa = pd.to_numeric(df.loc['Aktywa razem', :].str.replace(" ", ''))

    ROA_py = profit/aktywa
    ROA_aagr = aagr(ROA_py)
    dict['ROA'] = ROA_aagr[mean_periods:].mean()

#AAGR zysków
    AAGR = aagr(profit)
    dict['AAGR'] = AAGR[-cagr_period:].mean()

#stopa dywidendy
    liczba_akcji = clean_series(df.loc['Liczba akcji', :])
    dyw = clean_series(df.loc['Dywidenda', :]) * -1000 #kwota przeznaczona na dywidende w danym roku
    DPS = dyw/liczba_akcji #dividend per share
    DPS.name = 'DPS'

    share_prices = get_share_price(ticker)
    PPS = share_prices.groupby('rok')['Zamkniecie'].mean() #cena za akcje
    DY_table = pd.merge(DPS, PPS, how = 'inner', left_index = True, right_index = True)
    DY_table['DY'] = DY_table['DPS'] / DY_table['Zamkniecie']
    dict['DY'] = DY_table['DY'][-mean_periods:].mean()
    
#dynamika EPS 
    EPS = profit*1000/liczba_akcji
    dict['dynamika EPS'] = aagr(EPS)[-mean_periods:].mean()

#P/E
    PE = PPS[PPS.index <= 2024] / EPS
    dict['P/E'] = PE[-mean_periods:].mean()
    
#P/BV
    PBV = PPS[PPS.index <= 2024] / (equity_capital*1000/liczba_akcji)
    dict['P/BV'] = PBV[-mean_periods:].mean()
    
# std stop zwrotu
    price_pct = share_prices[share_prices['rok'] == 2024]['Zamkniecie'].pct_change()
    dict['std'] = price_pct.std()

#wsp beta 
    wig = get_share_price('wig')
    wig_pct = wig[wig['rok'] == 2024]['Zamkniecie'].pct_change()
    dict['beta'] = price_pct.cov(wig_pct)/wig_pct.var()
    
    
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
    
