import pandas as pd
import requests
from io import StringIO
import re

def GetData(company_name: str) -> pd.DataFrame | None:
    """
    Webscraping strony stockwatch.pl w celu zdobycia danych konkretnej spolki
    """


    url_mainpage = f'https://www.stockwatch.pl/gpw/{company_name},notowania,dane-finansowe.aspx'
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'} 
    header_new = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': url_mainpage,  
        'X-Requested-With': 'XMLHttpRequest' 
    }
    try:
        r = requests.get(url_mainpage, headers=header)
        r.raise_for_status()
        
        cid = re.search(r"var\s+companyId\s*=\s*'(\d+)';", r.text).group(1)
        isbank = re.search(r"var\s+isBank\s*=\s*'(\w+)';", r.text).group(1)

        url_api = f'https://www.stockwatch.pl/async/FinancialDataAsync.aspx?companyId={cid}&period=y&isBank={isbank}'
        r_new = requests.get(url_api, headers = header_new)
        df = pd.read_html(StringIO(r_new.text))[0]
        return df
    except Exception as e:
        print(f"Wystąpił błąd: {e}")
        return None


