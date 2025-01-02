
import time
import requests
#import urllib.parse
#import hashlib
#import hmac
#import base64
#import pandas
#import bisect
from newnodestouse import coordinator, converter, pricenode
from simulator import tradesimulator


# Get and process data
class datacollector:

    def __init__(self):
        # Predefined currency pairs. sets up needed variables and structures. Checks the status of the exchange and API
        self.currency_pairs = {'EURUSD', 'GBPUSD', 'USDJPY', 'AUDJPY', 'EURGBP', 'EURJPY', 'AUDUSD', 'EURAUD', 'GBPJPY',
                               'XBTAUD', 'XBTGBP', 'XBTJPY', 'XBTUSD', 'XBTEUR', 'ETHXBT', 'ETHEUR', 'ETHAUD', 'ETHGBP',
                               'ETHJPY', 'ETHUSD'}
        self.currencies = {'XBT', 'ETH', 'USD','EUR','GBP','AUD', 'JPY'}
        self.coinKeys = {}
        self.conversions = {}               #currency pairs are stored here
        self.coinstomake = []                    #prices here
        self.status = self.__healthcheck()
        if self.status == 'online':
            self.coins = self.__coinsinfo()
            self.__converterget()



    def __converterget(self):
        # Gets the conversion rates for the currency pairs
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
                fee = self.coins[coin][0]
                self.conversions[coin]= [close, fee]
            else:
                if coin[len(coin)-3:] in self.currencies:
                    self.coinstomake.append(coin)



    def coindatagrab(self, coin):
        # Gets the asking price, best offer price and fee for the coin
        price = requests.get('https://api.kraken.com/0/public/Ticker?pair={}'.format(coin))
        price = price.json()
        price = price['result']
        price = price[self.coins[coin][1]]
        asking = price['a'][0]
        bestoffer = price['b'][0]
        fee = self.coins[coin][0]
        return {coin: [asking, bestoffer, fee]}

    def __healthcheck(self):
        # Checks the status of the exchange
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
        # Gets the fees for the coins
        coinfees = {}
        coins = requests.get('https://api.kraken.com/0/public/AssetPairs?fees&altname')
        coins = coins.json()
        coins = coins['result']
        self.coinKeys = list(coins)
        for coin in self.coinKeys:
            pair = coins[coin]
            fees = pair['fees']
            fee = fees[0]
            altname = pair['altname']
            coinfees[altname] = [fee, coin]
        return coinfees

    def coinmakerinfo(self):
        return self.prices

    def convertermakerinfo(self):
        return self.conversions


    def reset(self):
        # Resets the datacollector
        self.coinKeys = {}
        self.conversions = {}               #currency pairs are stored here
        self.coinstomake = []                    #prices here
        self.status = self.__healthcheck()
        if self.status == 'online':
            self.coins = self.__coinsinfo()
            self.__converterget()



def coinsortfunc(coin):
    return (coin[:-3], coin[len(coin)-3:])

def swap(first, second, thelist):
    a = thelist.index(first)
    b = thelist.index(second)
    thelist[a], thelist[b] = thelist[b], thelist[a]

def main():
    worker = datacollector()
    brain = coordinator()
    sim  = tradesimulator()
    brain.getsimulator(sim)
    for i in range(275):
        print('wait')
        time.sleep(20)
        print('Ready')
        coinmaker = worker.coinstomake
        converterlist = worker.convertermakerinfo()
        converternodes = []
        gj_converter = converter('GBPJPY', 195.11, [0.20, 0.20])
        ga_converter = converter('GBPAUD', 2.00, [0.20, 0.20])
        converternodes.append(gj_converter)
        converternodes.append(ga_converter)
        for info in converterlist:
            converternodes.append(converter(info, converterlist[info][0], converterlist[info][1]))
        coinmaker.sort(key=coinsortfunc)
        #swap('KINEUR', 'KINTUSD', coinmaker)
        #swap('REPV2ETH', 'REPXBT', coinmaker)
        #swap('SCUSD', 'SCRTEUR', coinmaker)
        
        for converters in converternodes:
            brain.callconv(converters)
        for coin in coinmaker:
            nodeinfo = worker.coindatagrab(coin)
            key = list(nodeinfo.keys())
            key  = key[0]
            newnode = pricenode(key, nodeinfo[key][0], nodeinfo[key][1], nodeinfo[key][2])
            brain.coincall(newnode)
            newnode.sendinfo()
        brain.cointake(None)
        brain.hitstatus()
        brain.tradecheck()
        brain.reset()
        worker.reset()

if __name__ == '__main__':
    main()