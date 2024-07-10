import pandas as pd 
import numpy as np 
import yfinance as yf
from datetime import date
from dateutil.relativedelta import relativedelta

class Data: 
    def __init__(self, stock):
        self.stock = stock
        self.todayDate = date.today()
        self.decadeDate = self.todayDate - relativedelta(years= 10)
        self.company, self.company_info, self.data, self.latest_data = self.downloadData()
        self.fundamental_data = {
            'EPS': self.company.info['trailingEps'],
            'P/E Ratio': self.company.info['trailingPE'],
            'Revenue': self.company.info['totalRevenue'],
            'Debt-to-Equity Ratio': self.company.info['debtToEquity'],
            'Book Value': self.company.info['bookValue'],
            'Return on Equity': self.company.info['returnOnEquity']
        }

    #### Technical Indicators
    # moving average
    def moving_average(self, window = 50):
        return self.data['Close'].rolling(window=window).mean()
    
    # relative strength index
    def rsi(self,window = 14):
        delta = self.data['Close'].diff(1)
        gain = (delta.where(delta > 0, 0)).rolling(window = window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window = window).mean()
        rs = gain / loss 
        rsi = 100 - (100 / (1+rs))
        return rsi
    
    #moving average converegence divergence
    def macd(self,span1 = 12, span2 = 26, signal_span = 9):
        ema1 = self.data['Close'].ewm(span = span1, adjust = False).mean()
        ema2 = self.data['Close'].ewm(span = span2, adjust = False).mean()
        macd = ema1-ema2
        signal = macd.ewm(span = signal_span, adjust = False).mean()
        return macd, signal
    
    #### Statistical Features 

    # mean and Variance

    def mean_and_variance(self,window = 20):
        mean = self.data['Close'].rolling(window = window).mean()
        variance = self.data['Close'].rolling(window = window).mean()
        return mean, variance
    
    ### lagged features
    
    def create_lagged_features(self, lags = 5):
        for lag in range(1, lags + 1):
            self.data[f'lag_{lag}'] = self.data['Adj Close'].shift(lag)
        return self.data
    

    ## fundamental features 
    def pe_ratio(self):
        self.data['PE_ratio'] = self.fundamental_data['PE_ratio']
        return self.data
    def earnings_reports(self):
        self.data['Earnings'] = self.fundamental_data['Earnings']
        return self.data


    def downloadData(self):
        company = yf.Ticker(self.stock)
        companyInfo = company.info
        tenYearDailyData = yf.download(self.stock, start=str(self.decadeDate), end = str(self.todayDate), auto_adjust=True)
        currentData = company.history(period = "1d")
        return company, companyInfo,tenYearDailyData,currentData



data = Data("NVDA")