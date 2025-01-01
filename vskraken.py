import time
import requests
#import urllib.parse
#import hashlib
#import hmac
#import base64
import pandas
import bisect



 #get link market data
class datacollector:
        
    def __init__(self, target, intervals = [1, 3, 5, 15, 30]):
        #Creates a series of dataframes for each interval of time for the target coin 
        if type(target) != list:
            target = [target]                
        self.status = self.__healthcheck()
        self.intervals = intervals        
        self.coins = target
        self.__prices = {}
        if self.status == 'online':
            self.__getprices()
                
                
                
            
    def __healthcheck(self):
        #Checks the status of the Kraken API. Should return 'online' if the API is up and running
        health  = requests.get('https://api.kraken.com/0/public/SystemStatus')
        health = health.json()
        try:
            result = health['result']
            print(result)
            status = result['status']
            return status
        except:
            print('error')
            print(health)
    
    def __getprices(self):
        #Creates a dictionary of dataframes for each interval of time for the target
        templist = []
        for i in self.intervals:
            if i == 1 and 3 in self.intervals:   
                priceList = self.__get_price_list(i)
                templist = priceList.copy()
                self.__prices['{} minute interval'.format(i)] = pandas.DataFrame(priceList, columns=['time', 'opens', 'closes' ])
            elif i == 3 and 1 in self.intervals:                    
                priceList = self.__three_minute_list(templist)
                self.__prices['{} minute interval'.format(i)] = pandas.DataFrame(priceList, columns=['time', 'opens', 'closes' ])
            elif i == 3 and i not in self.intervals:
                priceList = self.__get_price_list(1)
                priceList = self.__three_minute_list(priceList)
                self.__prices['{} minute interval'.format(i)] = pandas.DataFrame(priceList, columns=['time', 'opens', 'closes' ])
            else:
                priceList = self.__get_price_list(i)
                self.__prices['{} minute interval'.format(i)] = pandas.DataFrame(priceList, columns=['time', 'opens', 'closes' ])
                
                    
    def __get_price_list(self, interval):
        #Gets the price data for the target coin at the specified interval
        priceList = []
        try:
            url = 'https://api.kraken.com/0/public/OHLC?pair={}USD&interval={}'.format((self.coins[0]), interval)
            prices = requests.get(url)
            prices = prices.json()
            results = prices['result']
            key = list(results.keys())
            key = key[0]
            coinData = results[key]                     
            for i in coinData:
                entry = [i[0], i[1], i[4]]
                priceList.append(entry)
        except Exception:
            print(prices['error'])
                
            
        return priceList
            
            
    def __three_minute_list(self, one_minute_list):
        #Converts a one minute list to a three minute list
        three_min_list = []
        for i in range(len(one_minute_list)//3):
            y = i*3
            z = y + 2
            entry = [one_minute_list[y][0], one_minute_list[y][1], one_minute_list[z][2]]
            three_min_list.append(entry)
        return three_min_list
        
    def getPriceData(self):
        return self.__prices
        
    def getIntervals(self):
        return self.intervals

            
        
            
                

class nerd:
    #This class is for the analysis of the data collected by the datacollector class. Ignore for now
    def __init__(self, datadict, intervals):
            
        self.intervals = intervals
        self.data = datadict
        self.processed = {}
        self.__macd()
        print(self.processed.values())
        self.planner()
        
    def __macd(self):
        for i in self.data.keys():
            frame = self.data.get(i)
            time = frame['time']
            twdays = frame['closes'].ewm(span=12, adjust=False, min_periods=12).mean()
            twsdays = frame['closes'].ewm(span=26, adjust=False, min_periods=26).mean()
            macd = twdays - twsdays
            tline = macd.ewm(span=9, adjust=False, min_periods=9).mean()        
            difference = macd - tline
            change = difference.diff()
            linechange = tline.diff()
            chartdata = pandas.concat([time, difference, macd, tline, change, linechange], axis=1)                
            chartdata.columns.values[1] = 'difference'
            chartdata.columns.values[2] = 'macd'
            chartdata.columns.values[3] = 'tline'
            chartdata.columns.values[4] = 'change'
            chartdata.columns.values[5] = 'linechange'
            self.processed[i+' data'] = chartdata
        return
        
        
    def planner(self, tline=0 ):
        for i in self.intervals:
            data = self.processed['{} minute interval data'.format(i)]
            bought = False
            buyspot = 0
            sellspot = 0
            money = 0
            trades = 0
            for j in range(len(data)):
                if bought == False:
                    if data.iloc[j,3] > tline:
                        if data.iloc[j, 1] < 0 and data.iloc[j, 4] > 0:
                            bought = True
                            buyspot = j
                            
                else:
                    if data.iloc[j, 1] > 0 and data.iloc[j, 4] < 0:
                        bought = False
                        sellspot = j
                        money = money + self.pf(buyspot, sellspot, i)
                        trades = trades + 1
            print('Total: ' + str(money))
            print('Trades: ' + str(trades))
        
    def plannertwo(self, tline=0):
        for i in self.intervals:
            data = self.processed['{} minute interval data'.format(i)]
            bought = False
            primed = False
            buyspot = 0
            sellspot = 0
            money = 0
            trades = 0
            for j in range(len(data)):
                if primed == False and bought == False:
                    if data.iloc[j, 3] < -0.07:
                        primed = True
                elif bought == False :
                    if data.iloc[j, 5] > 0:
                        bought = True
                        buyspot = j
                else:
                    if data.iloc[j, 5] < -0.005:
                        bought = False
                        primed = False
                        sellspot = j
                        money = money + self.pf(buyspot, sellspot, i)
                        trades = trades + 1                            
            print('Total: ' + str(money))
            print('Trades: ' + str(trades))
                
                
    def plannerthree(self, tline=0):
        for i in self.intervals:
            data = self.processed['{} minute interval data'.format(i)]
            bought = False
            primed = False
            buyspot = 0
            sellspot = 0
            money = 0
            trades = 0
            for j in range(len(data)):
                if primed == False and bought == False:
                    if data.iloc[j, 5] < 0:
                        primed = True
                elif bought == False :
                    if data.iloc[j, 5] > 0:
                        bought = True
                        buyspot = j
                else:
                    if data.iloc[j, 5] < -0.01:
                        bought = False
                        primed = False
                        sellspot = j
                        money = money + self.pf(buyspot, sellspot, i)
                        trades = trades + 1                            
            print('Total: ' + str(money))
            print('Trades: ' + str(trades))         
        
        
        
        
    def plannerfour(self):
        for i in self.intervals:
            data = self.processed['{} minute interval data'.format(i)]
            bought = False
            primed = False
            buyspot = 0
            sellspot = 0
            money = 0
            trades = 0
            counter = 0
            for j in range(len(data)):
                if primed == False and bought == False:
                    if data.iloc[j, 1] < 0:
                        primed = True
                elif bought == False :
                    if data.iloc[j, 1] > 0:
                        bought = True
                        buyspot = j
                elif counter < 3:
                    counter = counter + 1
                else:
                    if data.iloc[j, 1] < 0:
                        bought = False
                        primed = False
                        counter = 0
                        sellspot = j
                        money = money + self.pf(buyspot, sellspot, i)
                        trades = trades + 1                            
            print('Total: ' + str(money))
            print('Trades: ' + str(trades))             
        
    def multimacplanner(self):
        data = self.processed['1 minute interval data']
        bought = False
        buyspot = 0
        sellspot = 0
        money = 0
        trades = 0
        for j in range(len(data)):           
            if bought == False:
                if data.iloc[j, 1] < 0 and data.iloc[j, 4] > 0:
                        pass             
            return
        
    def __timematch(self, timestamp, intervals):
        search_in = self.processed['{} minute interval data'.format(intervals)]
        point = bisect.bisect_left(search_in, timestamp)
        if search_in[point] == timestamp:
            return int(point)
        else:
            return int(point) - 1
        
        
    def pf(self, buy, sell, interval):
        buyprice = self.data['{} minute interval'.format(interval)].iloc[buy, 2]
        sellprice = self.data['{} minute interval'.format(interval)].iloc[sell, 2]
        buyprice = float(buyprice)
        sellprice = float(sellprice)
        buyprice = (buyprice + (buyprice * 0.0026))
        sellprice = (sellprice - (sellprice * 0.0026))
        return sellprice - buyprice
        
    def __decider(self):
        return
        
    def practice(self):
        return

def main():
    coin = ['ada'.upper()]
    bot = datacollector(coin)
    data = bot.getPriceData()
    print(data)
#    intervals = bot.getIntervals()
#   bot2 = nerd(data, intervals)
    
if __name__ == '__main__':
    main()


#test zone
#coin = ['link']
#test = 'https://api.kraken.com/0/public/Ticker?pair={}USD'.format(coin[0])
#print(test)
