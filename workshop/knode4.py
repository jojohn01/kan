import time
import requests
#import urllib.parse
#import hashlib
#import hmac
#import base64
#import pandas
#import bisect
from newnodestouse import Acoordinator, Aconverter, pricenode
from simulator import arbitrator
from knode2 import datacollector, coinsortfunc
import asyncio
import multiprocessing



def coinsortfunc(coin):
    return (coin[:-3], coin[len(coin)-3:])

class fastdatacollector:
    currency_pairs = {'EURUSD', 'GBPUSD', 'USDJPY', 'AUDJPY', 'EURGBP', 'EURJPY', 'AUDUSD', 'EURAUD', 'GBPJPY',
                               'XBTAUD', 'XBTGBP', 'XBTJPY', 'XBTUSD', 'XBTEUR', 'ETHXBT', 'ETHEUR', 'ETHAUD', 'ETHGBP',
                               'ETHJPY', 'ETHUSD'}
    currencies = {'XBT', 'ETH', 'USD','EUR','GBP','AUD', 'JPY', 'CAD'}

    finalized_pairs = {}

    def __init__(self):
        # Predefined currency pairs. sets up needed variables and structures. Checks the status of the exchange and API
        self.fiatpairs = {}
        self.groups = {}
        self.altKeys = None
        self.coinKeys = None
        self.alttonorm = {}
        if self.healthcheck() == 'online':
            self.fiatfinder()
            print('wait')
            time.sleep(5)
            print('Ready to refresh')

    def allcoininfo(self):
        #Gets all the coin info at once for faster parallel processing later
        coins = requests.get('https://api.kraken.com/0/public/AssetPairs')
        coins = coins.json()
        coins = coins['result']
        alts = []
        self.coinKeys = sorted(coins.keys(), key=coinsortfunc)
        for coin in coins:
            alt = coins[coin]['altname']
            self.alttonorm[alt] = coin
            alts.append(alt)
        self.altKeys = sorted(alts, key=coinsortfunc)
        return self.coinKeys

    def groupcoins(self):
        #Groups coins by their base currency
        current = None
        pairs = []
        for name in self.coinKeys:
            if name[:3] not in self.currencies:
                if not current:
                    current = name[0:-3]
                if name[0:-3] != current:
                    self.groups[current] = pairs
                    pairs = []
                    current = name[0:-3]
                pairs.append(name)
        self.groups[current] = pairs
        return self.groups

    def multiarbchecker(self):
        #performs arbitrage check on all coins at once for faster processing
        info = requests.get('https://api.kraken.com/0/public/Ticker')
        info = info.json()
        info = info['result']
        print(info)
        
        for i in self.groups:
            print(i)
            for i in self.groups[i]:
                if i in self.alttonorm:
                    print(i, self.alttonorm[i])
                else:
                    if i in self.coinKeys:
                        print("{} in coinKeys, but not in groups".format(i))
                    else:
                        print('{} not found'.format(i))
                    #info = requests.get('https://api.kraken.com/0/public/AssetPairs?pair={}'.format(i))
                    #info = info.json()
                    #info = info['result']
                    #print(info)



    def healthcheck(self):
        # Checks the status of the exchange and API
        status = requests.get('https://api.kraken.com/0/public/Time')
        if status.status_code == 200:
            return 'online'
        else:
            return 'offline'

    def fiatfinder(self):
        # Finds all the fiat currencies available
        coins = requests.get('https://api.kraken.com/0/public/Ticker')
        coins = coins.json()
        coins = coins['result']
        for i in self.currency_pairs:
            likely = None
            for j in coins:
                if i[:-3] in j and i[-3:] in j:
                    if not likely or 'Z' not in likely:
                        likely = j
            self.fiatpairs[i] = likely #stores the likely fiat pair code for the currency pair
        print(self.fiatpairs)
                    


collector = fastdatacollector()
collector.allcoininfo()
collector.groupcoins()
collector.fiatfinder()
collector.multiarbchecker()