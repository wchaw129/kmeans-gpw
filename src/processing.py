import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt



def read_file(
        company_name: str
) -> pd.DataFrame | None:
    
    DIR = rf'../data/raporty/{company_name}.csv' 
    
    try:
        df = pd.read_csv(DIR, sep = ',')
        df = df.set_index('Dane / Okres').iloc[:, 2:]
        df.columns = df.columns.str.slice(-4).astype(int)
        return df
    except Exception as e:
        print(e)
        return None
    


def clean_series(
    series: pd.Series
) -> pd.Series:
    return pd.to_numeric(series.str.replace(' ', ''))



def set_plot_font():
    plt.rcParams['font.family'] = 'serif' 
    plt.rcParams['font.serif'] = ['Times New Roman'] 

def set_plot_style():
    sns.set_theme(
        style="whitegrid",      
        context="paper",        
        palette="colorblind",   
        font_scale=1.2          
    )


def save_chart(
        chart_name: str
):
    plt.savefig(rf'charts/{chart_name}.png', dpi = 300, bbox_inches='tight')