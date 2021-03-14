import pandas as pd 
import numpy as np 
import datetime as dt 
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt 
from matplotlib import style
import matplotlib.dates as mdates 

class MACD():
    def __init__(self,stock,start,end):
        self.stock = stock
        self.start = start
        self.end =end 
    def fetch_data(self):
        """
        clean data
        """
        df=pdr.get_data_yahoo(self.stock,self.start,self.end)
        ema1=12
        ema2=26
        df["ema_12"]=df["Adj Close"].ewm(span=ema1).mean()
        df["ema_26"]=df["Adj Close"].ewm(span=ema2).mean()

        ## dif and macd
        df["dif"]=df["ema_12"]-df["ema_26"]
        df["macd"]=df["dif"].ewm(span=9).mean()
        df["barchart"]=df["dif"]-df["macd"]
        df=df[['Adj Close',"ema_12","ema_26","dif","macd",'barchart']]  ##清理資料
        self.df = df 
        return self.df
    def backtest_strategy(self):
        """
        交易策略: 若DIF 由下穿越到MACD線 "上方" 則會有一波漲幅,此時進場
        若DIF 由上穿越到MACD線 "下方"  則會有一波跌幅,此時出場..... macd收斂至dif的感覺
        """
        percentage=[]
        pos=0
        num=0
        for i in self.df.index:
            num+=1
            close=self.df['Adj Close'][i]
            macd=self.df['macd'][i]
            dif=self.df['dif'][i]
            if (dif>macd and pos==0):
                pos=1
                bp=close
                print("on date "+str(i)+" buying  now  at price "+str(bp))
            elif (dif<macd and pos==1):
                pos=0
                sp=close
                pc=(sp/bp-1)*100
                percentage.append(pc)
                print("on date "+str(i)+"selling now at price "+str(sp))
            elif (num==self.df['Adj Close'].count()-1 and pos ==1):
                pos=0
                sp=close
                pc=(sp/bp-1)*100
                percentage.append(pc)
                print("on date "+str(i)+"selling now at price "+str(sp))
                break
        self.percentage = percentage
        return self.percentage
    def summary(self):
        gain=0
        ng=0   ##numbers of gain
        losses=0  
        nl=0   ## numbers of losses
        totalR=1  
        for i in self.percentage:
            totalR=totalR*((i/100)+1)
            if (i>0):
                gain+=i 
                ng+=1
            else:
                losses+=i 
                nl+=1
        if(ng>0):
            avggain=gain/ng
            maxr=str(max(self.percentage))
        else:
            avggain=0
            maxr='undefined'
        if(nl>0):
            avgloss=losses/nl
            maxl=str(min(self.percentage))
            ratio=str(-avggain/avgloss)
        else:
            avgloss=0
            maxl='undefined'
            ratio='inf'
        if(ng>0 or nl>0):
            battingave=ng/(ng+nl)
        else:
            battingave=0
        print("Results for "+ self.stock +" going back to "+str(self.df.index[0])+", Sample size: "+str(ng+nl)+" trades")
        print("Batting Avg: "+ str(battingave))
        print("Gain/loss ratio: "+ ratio)
        print("Average Gain: "+ str(avggain))
        print("Average Loss: "+ str(avgloss))
        print("Max Return: "+ maxr)
        print("Max Loss: "+ maxl)
        print("Total return over "+str(ng+nl)+ " trades: "+ str(totalR)+"%" )
    def plot_data(self) : 
        style.use('classic')
        y4=self.df["Adj Close"]
        y5=self.df["ema_12"]
        y6=self.df["ema_26"]
        y1=self.df["dif"]
        y2=self.df["macd"]
        y3=self.df['barchart']
        x=self.df.index.map(mdates.date2num)

        plt.subplot2grid((6,1),(4,0),rowspan=2,colspan=1)
        plt.plot(x,y1,label="short term",color='b')
        plt.plot(x,y2,label="long term",color='r')
        plt.bar(x,y3,label='barchart',color='green')
        plt.xlabel("time")
        plt.legend()

        plt.subplot2grid((6,1),(0,0),rowspan=4,colspan=1)
        plt.plot(x,y4,label="stock's price",color='k')
        plt.plot(x,y5,label="ma_n=12")
        plt.plot(x,y6,label="ma_n=26")
        plt.title("macd pratice")
        plt.xlabel("time")
        plt.ylabel("value")

        plt.legend()
        plt.show()


s=dt.datetime(2020,1,1)
e=dt.datetime.now()
stock ="aapl"
 
strategy = MACD(stock,start=s,end=e)
stock_df = strategy.fetch_data()
percentage = strategy.backtest_strategy()
strategy.summary()
strategy.plot_data()