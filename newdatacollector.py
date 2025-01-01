import time
import requests
#import urllib.parse
#import hashlib
#import hmac
#import base64
import pandas
import bisect



 #get link market data
class Training_data_collector:
        
    def __init__(self, target, intervals = [1, 3, 5, 15, 30]):
        #Creates a series of dataframes for each interval of time for the target coin 
        if type(target) != list:
            target = [target]                
        self.status = self.__healthcheck()
        self.intervals = intervals        
        self.coins = target
        self.__prices = {}
        if self.status == 'online':
            for coin in self.coins:
                self.__getprices(coin)
                print('Resting for 1 second')
                time.sleep(1)
                
                
                
            
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
    
    def __getprices(self, coin):
        #Creates a dictionary of dataframes for each interval of time for the target
        templist = []
        temp_dict = {}
        for i in self.intervals:
            args = (i, coin)
            if i == 1 and 3 in self.intervals:   
                priceList = self.__get_price_list(*args)
                templist = priceList.copy()
                temp_dict['{} minute interval'.format(i)] = pandas.DataFrame(priceList, columns=['time', 'opens', 'high', 'low', 'closes' ])
            elif i == 3 and 1 in self.intervals:                    
                priceList = self.__three_minute_list(templist)
                temp_dict['{} minute interval'.format(i)] = pandas.DataFrame(priceList, columns=['time', 'opens', 'high', 'low', 'closes' ])
            elif i == 3 and i not in self.intervals:
                priceList = self.__get_price_list(1, coin)
                priceList = self.__three_minute_list(priceList)
                temp_dict['{} minute interval'.format(i)] = pandas.DataFrame(priceList, columns=['time', 'opens', 'high', 'low', 'closes' ])
            else:
                priceList = self.__get_price_list(*args)
                temp_dict['{} minute interval'.format(i)] = pandas.DataFrame(priceList, columns=['time', 'opens', 'high', 'low', 'closes' ])
        self.__prices[coin] = temp_dict
                
                    
    def __get_price_list(self, interval, coin):
        #Gets the price data for the target coin at the specified interval
        priceList = []
        try:
            url = 'https://api.kraken.com/0/public/OHLC?pair={}USD&interval={}'.format((coin), interval)
            prices = requests.get(url)
            prices = prices.json()
            results = prices['result']
            key = list(results.keys())
            key = key[0]
            coinData = results[key]                     
            for i in coinData:
                entry = [i[0], i[1], i[2], i[3], i[4]]
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
            high = max(float(one_minute_list[y][2]), float(one_minute_list[y+1][2]), float(one_minute_list[y+2][2]))
            low = min(float(one_minute_list[y][3]), float(one_minute_list[y+1][3]), float(one_minute_list[y+2][3]))
            entry = [one_minute_list[y][0], one_minute_list[y][1], high, low, one_minute_list[z][2]]
            three_min_list.append(entry)
        return three_min_list
        
    def getPriceData(self):
        return self.__prices
        
    def getIntervals(self):
        return self.intervals

            
if __name__ == '__main__':
    coins = ['XBT', 'ETH', 'MORPHO', 'ADA', 'XRP', 'SOL', 'PEPE', 'DOGE', 'DRIFT', 'PONKE', 'BONK']
    data = Training_data_collector(coins)
    print(data.getPriceData())
