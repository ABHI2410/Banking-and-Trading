import pandas as pd 
import pandas_ta
import numpy as np 
import yfinance as yf
from datetime import date
from dateutil.relativedelta import relativedelta

class Data: 
    def __init__(self):
        sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
        sp500['Symbol'] = sp500['Symbol'].str.replace('.','-')
        self.tickers: list = sp500['Symbol'].unique().tolist()
        self.todayDate: date = date.today()
        self.decadeDate : date = self.todayDate - relativedelta(years= 10)
        self.data = (yf.download(tickers=self.tickers,start = self.decadeDate,end = self.todayDate)).stack(future_stack=True)
        self.data.index.names = ['date', 'ticker']
        self.data.columns = self.data.columns.str.lower()
        self.tech_indicators()

    #### Technical Indicators
    def compute_atr(self, stock_data):
        atr = pandas_ta.atr(high = stock_data['high'],
                            low = stock_data['low'],
                            close= stock_data['close'],
                            length=16)
        return atr.sub(atr.mean()).div(atr.std())
    
    def compute_macd(self, close):
        macd = pandas_ta.macd(close=close, length = 20).iloc[:,0]
        return macd.sub(macd.mean()).div(macd.std())
    
    def tech_indicators(self):
        self.data['garman_klass_vol'] = ((np.log(self.data['high']) - np.log(self.data['low']))**2)/2 - ((2*np.log(2)-1)*(np.log(self.data['adj close'])-np.log(self.data['open']))**2) 
        self.data['rsi'] = self.data.groupby(level = 1)['adj close'].transform(lambda x: pandas_ta.rsi(close = x, lemgth = 20))
        self.data['bb_low'] = self.data.groupby(level = 1)['adj close'].transform(lambda x: pandas_ta.bbands(close = np.log(x), lemgth = 20).iloc[:,0])
        self.data['bb_mid'] = self.data.groupby(level = 1)['adj close'].transform(lambda x: pandas_ta.bbands(close = np.log(x), lemgth = 20).iloc[:,1])
        self.data['bb_high'] = self.data.groupby(level = 1)['adj close'].transform(lambda x: pandas_ta.bbands(close = np.log(x), lemgth = 20).iloc[:,2])
        self.data['atr'] = self.data.groupby(level = 1,group_keys=False).apply(self.compute_atr)
        self.data['macd'] = self.data.groupby(level = 1,group_keys=False)['adj close'].apply(self.compute_macd)
        self.data['dollar_volume'] = (self.data['adj close'] * self.data['volume'])/1e6

    def agg_month(self):
        last_cols: list = [col for col in self.data.columns.unique(0) if col not in ['dollar_volume', 'volumn', 'open', 'high', 'low', 'close']]
        return pd.concat([self.data.unstack('ticker')['dollar_volume'].resample('ME').mean().stack('ticker',future_stack=True).to_frame('dollar_volume'),
                   self.data.unstack()[last_cols].resample('ME').last().stack('ticker',future_stack=True)],
                   axis=1).dropna()
    
    def rolling_avg(self,month_agg):
        month_agg['dollar_volume'] = month_agg.loc[:,'dollar_volume'].unstack('ticker').rolling(10*12).mean().stack(future_stack=True)
        return monthly_aggregate
    
    def top_150(self,month_agg):
        month_agg['dollar_vol_rank'] = month_agg.groupby('date')['dollar_volume'].rank(ascending=False)
        return month_agg[month_agg['dollar_vol_rank']<150].drop(['dollar_volume', 'dollar_vol_rank'],axis =1)


if __name__ == "__main__":
    data = Data()
    monthly_aggregate = data.agg_month()
    monthly_aggregate = data.rolling_avg(monthly_aggregate)
    top_150_liq_stocks = data.top_150(monthly_aggregate)
    print(top_150_liq_stocks)