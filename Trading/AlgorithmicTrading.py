from statsmodels.regression.rolling import RollingOLS
import pandas_datareader.data as web
import matplotlib as plt
import statsmodels.api as sm
import pandas as pd
import numpy as np
import datetime as dt
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
sp500['Symbol'] = sp500['Symbol'].str.replace('.','-')
tickers: list = sp500['Symbol'].unique().tolist()

end_date: str = '2024-08-16'
start_date = pd.to_datetime(end_date)-pd.DateOffset(365*10)

df = yf.download(tickers=tickers,
                 start = start_date,
                end =end_date)
df = df.stack()
print(df)