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

class otfdatacollector(datacollector):

    def __init__(self):
        # Predefined currency pairs. sets up needed variables and structures. Checks the status of the exchange and API
        self.currency_pairs = {'EURUSD', 'GBPUSD', 'USDJPY', 'AUDJPY', 'EURGBP', 'EURJPY', 'AUDUSD', 'EURAUD', 'GBPJPY',
                               'XBTAUD', 'XBTGBP', 'XBTJPY', 'XBTUSD', 'XBTEUR', 'ETHXBT', 'ETHEUR', 'ETHAUD', 'ETHGBP',
                               'ETHJPY', 'ETHUSD'}
        self.currencies = {'XBT', 'ETH', 'USD','EUR','GBP','AUD', 'JPY'}
        self.coinKeys = {}
        self.conversions = {}               #currency pairs are stored here
        self.coinstomake = []                    #prices here
        self.status = self.healthcheck()
        if self.status == 'online':
            self.coins = self.coinsinfo()
            #self.converterget()


    def converterget(self, pair):
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



def main():
    worker = otfdatacollector()
    brain = Acoordinator()
    sim = arbitrator()
    brain.getsimulator(sim)
    for i in range(1):
        print('wait')
        time.sleep(5)
        print('Ready')
        coinmaker = worker.coinstomake
        converterlist = worker.convertermakerinfo()
        converternodes = []
        gj_converter = Aconverter('GBPJPY', 195.11, [0.20, 0.20])
        ga_converter = Aconverter('GBPAUD', 2.00, [0.20, 0.20])
        converternodes.append(gj_converter)
        converternodes.append(ga_converter)
        for info in converterlist:
            converternodes.append(Aconverter(info, converterlist[info][0], converterlist[info][1]))
        coinmaker.sort(key=coinsortfunc)

if __name__ == '__main__':
    main()