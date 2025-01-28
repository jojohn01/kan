
#import time
import requests
#import urllib.parse
#import hashlib
#import hmac
#import base64
#import pandas
#import bisect
from krakennodeapproach import coordinator, converter, pricenode



# Get and process data
class datacollector:

    def __init__(self):
        
        self.currency_pairs = {'EURUSD', 'GBPUSD', 'USDJPY', 'AUDJPY', 'EURGBP', 'EURJPY', 'AUDUSD', 'EURAUD', 'GBPJPY'}
        self.currencies = ['USD','EUR','GBP','AUD', 'JPY']
        self.coinKeys = {}
        self.conversions = {}               #currency pairs are stored here
        self.prices = {}                    #prices here
        self.status = self.__healthcheck()
        if self.status == 'online':
            self.coins = self.__coinsinfo()
            self.__priceget()
            #self.__price_organize()

    def __price_organize(self):
        grouped = []
        coins = self.prices
        previous = ''
        temp = []
        for coin in coins:
            name = coin[0:len(coin)-3]
            if previous == '':
                previous = name
            if name != previous:
                grouped.append(temp)
                previous = coin
                temp = []
            temp.append({coin : coins[coin]})
        print(grouped)


    def __priceget(self):
        time = requests.get('https://api.kraken.com/0/public/Time')
        time = time.json()
        time = time['result']
        time = time['unixtime']
        for coin in self.coins:
            if coin in self.currency_pairs:
                price = requests.get('https://api.kraken.com/0/public/OHLC?pair={}&since={}'.format(coin, time))
                price = price.json()
                price = price['result']
                key = list(price.keys())
                key = key[0]
                close = price[key][0][4]
                fee = self.coins[coin]
                self.conversions[coin]= [close, fee]
            else:
                for bill in self.currencies:
                    if bill in coin[len(coin)-3:]:
                        price = requests.get('https://api.kraken.com/0/public/OHLC?pair={}&since={}'.format(coin, time))
                        price = price.json()
                        price = price['result']
                        key = list(price.keys())
                        key = key[0]
                        close = price[key][0][4]
                        fee = self.coins[coin]
                        self.prices[coin] = [close, fee]

    def __healthcheck(self):
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

    
    def __coinsinfo(self):
        coinfees = {}
        coins = requests.get('https://api.kraken.com/0/public/AssetPairs?fees&altname')
        coins = coins.json()
        coins = coins['result']
        self.coinKeys = coins.keys()
        self.coinKeys = list(coins)
        for coin in self.coinKeys:
            pair = coins[coin]
            fees = pair['fees']
            fee = fees[0]
            altname = pair['altname']
            coinfees[altname] = fee
        return coinfees

    def coinmakerinfo(self):
        return self.prices

    def convertermakerinfo(self):
        return self.conversions



def coinsortfunc(coin):
    return coin.pair


def main():
    worker = datacollector()
    print('Ready')
    coinmaker = worker.coinmakerinfo()
    converterlist = worker.convertermakerinfo()
    brain = coordinator()
    coinnodes = []
    converternodes = []
    gj_converter = converter('GBPJPY', 156.45, [0.20, 0.20])
    ga_converter = converter('GBPAUD', 1.88, [0.20, 0.20])
    converternodes.append(gj_converter)
    converternodes.append(ga_converter)
    for info in coinmaker:
        coinnodes.append(pricenode(coinmaker[info][0], info, coinmaker[info][1]))
    for info in converterlist:
        converternodes.append(converter(info, converterlist[info][0], converterlist[info][1]))
    coinnodes.sort(key=coinsortfunc)
    coinnodes[122], coinnodes[124] = coinnodes[124], coinnodes[122]
    for converters in converternodes:
        brain.callconv(converters)
    for coin in coinnodes:
        brain.coincall(coin)
    converternodes.append(None)
    for nodes in coinnodes:
        nodes.sendinfo()



main()