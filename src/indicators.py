import pandas as pd
from io import StringIO
import requests 
import time
from src.processing import read_file, clean_series


def get_income(
        company_name: str,
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



def get_dividend_per_share(
        company_name: str,
) -> pd.Series:
    
    df = read_file(company_name)
    shares_n = clean_series(df.loc['Liczba akcji', :])
    dyw = clean_series(df.loc['Dywidenda', :]) * -1000 #kwota przeznaczona na dywidende w danym roku
    DPS = dyw/shares_n #dividend per share
    DPS.name = 'DPS'
    return DPS



def count_indicators(
        company_name: str,
        ticker: str,
        mean_periods: int,
        aagr_period: int,
        base_year: int
) -> dict | None:
    
    result_dict = {}

    df = read_file(company_name)

#ROE
    profit = get_income(company_name) #zysk netto
    equity_capital = clean_series(df.loc['Kapitał własny', :]) #kapital wlasny
    ROE_py = profit/equity_capital #ROE per year
    result_dict['ROE'] = ROE_py[-mean_periods:].mean()

#ROA 
    if 'Suma bilansowa' in df.index:
        assets = clean_series(df.loc['Suma bilansowa', :])
    else: 
        assets = clean_series(df.loc['Aktywa razem', :])

    ROA_py = profit/assets
    result_dict['ROA'] = ROA_py[-mean_periods:].mean()

#AAGR zysków
    AAGR = aagr(profit)
    result_dict['AAGR'] = AAGR[-aagr_period:].mean()

#stopa dywidendy
    DPS = get_dividend_per_share(company_name=company_name)

    share_prices = get_share_price(ticker)
    PPS = share_prices.groupby('rok')['Zamkniecie'].mean() #cena za akcje
    DY_table = pd.merge(DPS, PPS, how = 'inner', left_index = True, right_index = True)
    DY_table['DY'] = DY_table['DPS'] / DY_table['Zamkniecie']
    result_dict['DY'] = DY_table['DY'][-mean_periods:].mean()
    
#dynamika EPS 
    shares_n = clean_series(df.loc['Liczba akcji', :])
    EPS = profit*1000/shares_n
    result_dict['dynamika EPS'] = aagr(EPS)[-mean_periods:].mean()

#P/E
    PE = PPS[PPS.index <= base_year] / EPS
    result_dict['P/E'] = PE[-mean_periods:].mean()
    
#P/BV
    PBV = PPS[PPS.index <= base_year] / (equity_capital*1000/shares_n)
    result_dict['P/BV'] = PBV[-mean_periods:].mean()
    
# std stop zwrotu
    price_pct = share_prices[share_prices['rok'] == base_year]['Zamkniecie'].pct_change()
    price_pct.name = 'price_pct'
    result_dict['std'] = price_pct.std()

#wsp beta 
    wig = get_share_price('wig')
    wig_pct = wig[wig['rok'] == base_year]['Zamkniecie'].pct_change()
    wig_pct.name = 'wig_pct'
    aligned_returns = pd.merge(wig_pct, price_pct, left_index=True, right_index=True, how='inner')
    aligned_returns = aligned_returns.dropna() 
    cov = aligned_returns['price_pct'].cov(aligned_returns['wig_pct'])
    var = aligned_returns['wig_pct'].var()
    result_dict['beta'] = cov/var
    
    
    return result_dict


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
    
