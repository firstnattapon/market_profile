import ccxt
import datetime as dt
from datetime import  datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from sklearn.preprocessing import  MinMaxScaler
from market_profile import MarketProfile
pd.set_option("display.precision", 6)
# sns.set_style("whitegrid")

class Run_model(object) :
    def __init__(self ):
        self.pair_data  = 'BTC/USDT'
        self.timeframe  = "1h"
        self.loop_start = dt.datetime(2020, 7 , 1  , 0, 0)
        self.limit     = 5000
        self.rolling = 168
        self.broker = 'binance'
 
    def mp (self):
        exchange = getattr(ccxt , self.broker)
        exchange = exchange({'apiKey': '' ,'secret': ''  , 'enableRateLimit': True }) 
        ohlcv =exchange.fetch_ohlcv(self.pair_data, self.timeframe , limit=self.limit )
        ohlcv = exchange.convert_ohlcv_to_trading_view(ohlcv)
        df =  pd.DataFrame(ohlcv)
        df.t = df.t.apply(lambda  x :  datetime.fromtimestamp(x))
        df =  df.set_index(df['t']) ; df = df.drop(['t'] , axis= 1 )
        df = df.rename(columns={"o": "Open", "h": "High"  , "l": "Low", "c": "Close" , "v": "Volume"})
        dataset = df  ; dataset = dataset.dropna() ; dataset = dataset[self.loop_start:]
        dataset['ohlc'] = (dataset.Open + dataset.High +  dataset.Low  + dataset.Close) / 4
        dataset['pct_change'] = dataset.ohlc.pct_change()
        dataset['x'] =  np.where( dataset['pct_change'] > 0 , dataset['pct_change'] , 0 )
        dataset['y'] =  np.where( dataset['pct_change'] < 0 , abs(dataset['pct_change']) , 0 )
        dataset['x-cum'] = np.cumsum(dataset['x'])
        dataset['y-cum'] = np.cumsum(dataset['y']) 
        dataset['x-ber'] = dataset['x'].rolling(self.rolling).mean()
        dataset['y-ber'] = dataset['y'].rolling(self.rolling).mean()
        dataset['n-ber'] =   dataset['x-ber'] - dataset['y-ber']
        dataset['sp']     = dataset['x-cum'] - dataset['y-cum']
        sc = MinMaxScaler(feature_range=(0,1))
        dataset['sp']  = sc.fit_transform(dataset[['sp']])
        mp = MarketProfile(dataset)
        mp_slice = mp[dataset.index.min():dataset.index.max()]
        fig , (ax1, ax2 ,ax3) = plt.subplots(3 , figsize=(16, 24))
        ax1.plot(dataset.Close , color='m'  , ls ='-.')
        ax1.axhline(y = mp_slice.poc_price , color='k' , ls ='--' ,lw= 2.5)
        ax1.axhline(y = mp_slice.value_area[0] , color='r' , ls ='--' ,lw= 2.5)
        ax1.axhline(y = mp_slice.value_area[1] , color='r', ls ='--' ,lw= 2.5)
        ax1.axhline(y = mp_slice.profile_range[0] , color='g')
        ax1.axhline(y = mp_slice.profile_range[1] , color='g')
        ax1.axhline(y = mp_slice.balanced_target , color='c')
        # ax1.axhline(y = mp_slice.initial_balance()[0] , color='c')
        # ax1.axhline(y = mp_slice.initial_balance()[1] , color='c');
        for i in mp_slice.high_value_nodes.index :
            ax1.axhline(y = i , color='k' , lw=0.20 ,  ls ='-.')
        # for i in mp_slice.low_value_nodes.index:    
        #     ax1.axhline(y = i , color='m'  , lw=0.30 ,  ls ='-.');

        ax2.plot(dataset['sp']  , color='k', lw=1 , ls ='-.');
        ax2.plot(dataset['x-cum']  , color='g', lw=1 , ls ='-.')
        ax2.plot(dataset['y-cum']  , color='r', lw=1 , ls ='-.')
        ax2.axhline()

        ax3.plot(dataset['x-ber'] , color='g', lw=1 , ls ='-.')
        ax3.plot(dataset['y-ber'] , color='r', lw=1 , ls ='-.')
        ax3.plot(dataset['n-ber'] , color='k', lw=1 , ls ='-.')
        ax3.axhline()
        st.pyplot()

        st.write("Initial balance: {}".format(mp_slice.initial_balance()) )
        st.write("Opening range: {}".format(mp_slice.open_range()))
        st.write("POC: {}".format(mp_slice.poc_price))
        st.write("Profile range: {}".format(mp_slice.profile_range))
        st.write("Value area: {}".format(mp_slice.value_area))
        st.write("Balanced Target: {}".format(mp_slice.balanced_target))


if __name__ == "__main__":
    model =  Run_model()
    model.broker =      st.sidebar.text_input("exchange", 'binance')
    model.pair_data =   st.sidebar.text_input("data", 'BTC/USDT')
    model.timeframe =   st.sidebar.selectbox('timeframe',('1h', '4h' ,'1d' ,'1w'))
    model.loop_start =  np.datetime64(st.sidebar.date_input('loop_start', value= dt.datetime(2020, 7, 1, 0, 0)))
    model.limit     =  st.sidebar.number_input('limit' , value= 5000 )
    model.rolling = st.sidebar.number_input('rolling' , value= 168 )
    mp = model.mp()
