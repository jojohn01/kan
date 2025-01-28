import requests
import asyncio
import time

# This will contain my third generation of objects fr ththe simulator

def coinsortfunc(coin):
    return (coin[:-3], coin[len(coin)-3:])

class coinpair:

    def __init__(self, pair, fee):
        self.pair = pair
        self.fee = float(fee)/100
        #self.fee = 0.1/100
        
    
    def getpair(self):
        return self.pair

    def getcoin(self):
        return self.pair[0:-3]

    def getcurrency(self):
        return self.pair[-3:0]

    async def getprices(self):
        price = requests.get("https://api.kraken.com/0/public/Depth?pair={}&count=1".format(self.pair))
        price = price.json()
        key = list(price['result'].keys())[0]
        try:
            buycost = price['result'][key]['asks'][0][0]
            sellprice = price['result'][key]['bids'][0][0]
        except:
            return
        return float(buycost), float(sellprice)

    async def getbuyprice(self):
        price = requests.get("https://api.kraken.com/0/public/Depth?pair={}&count=1".format(self.pair))
        price = price.json()
        key = list(price['result'].keys())[0]
        cost = price['result'][key]['asks'][0][0]
        return float(cost)

    async def getsellprice(self):
        price = requests.get("https://api.kraken.com/0/public/Depth?pair={}&count=1".format(self.pair))
        price = price.json()
        cost = price['result'][self.pair]['bids'][0][0]
        return float(cost)
    
    def getfee(self):
        return self.fee

    async def convert(self):
        rate = await self.getbuyprice()
        return float(rate)


class collector:
    currency_pairs = {'EURUSD', 'GBPUSD', 'USDJPY', 'AUDJPY', 'EURGBP', 'EURJPY', 'AUDUSD', 'EURAUD', 'GBPJPY',
                               'XBTAUD', 'XBTGBP', 'XBTJPY', 'XBTUSD', 'XBTEUR', 'ETHXBT', 'ETHEUR', 'ETHAUD', 'ETHGBP',
                               'ETHJPY', 'ETHUSD'}
    currencies = {'XBT', 'ETH', 'USD','EUR','GBP','AUD', 'JPY', 'CAD', 'POL', 'DAI'}

    def __init__(self):
        self.coinKeys = None
        self.keyset = None
        self.conversions = {}               #currency pairs are stored here
        self.coins = {}                     #prices here
        self.status = self.healthcheck()
        self.groups = {}
        if self.status == 'online':
            pass
        
    
    def coingen(self):
        # gets all the coin names from the API
        coins = requests.get('https://api.kraken.com/0/public/AssetPairs?')
        coins = coins.json()
        coins = coins['result']
        alts = []
        for coin in coins:
            alt = coins[coin]['altname']
            self.coins[alt] = coinpair(alt, coins[coin]['fees'][0][1]) # this is where the highest fees are set. That is my current level in the exchange. Planned updates to make fees easier to work with

            alts.append(coins[coin]['altname'])
        self.coinKeys = alts
        self.coinKeys.sort(key=coinsortfunc)
        self.keyset = set(self.coinKeys)
        return self.coinKeys

    def healthcheck(self):
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

    
    def makecoinpairs(self):
        pairs = []
        for name in self.coinKeys:
            pair = coinpair(name, self.coinKeys[name])
            pairs.append(pair)
        return pairs
    
    def grouper(self):
        current = None
        pairs = []
        for name in self.coinKeys:
            if name[:3] not in self.currencies:
                if not current:
                    current = name[0:-3]
                if current and name[0:-3] != current:
                    self.groups[current] = pairs
                    current = name[0:-3]
                    pairs = []
                pairs.append(name)
        self.groups[current] = pairs


    def forwardprofit(self, prices1, prices2, straight_conversions, fee, conversion_fee): # modify this function to manually change fees. Planned update shoudl make this better
        price1= prices1[0]
        price4 = prices2[1]
        conversion_buy = straight_conversions[0]
        conversion_sell = straight_conversions[1]
        arbprice = (price4 * (1 - fee))/(price1 * (1 + fee))
        profit = arbprice - conversion_sell
        profit_percent =  (arbprice / conversion_sell) - 1
        cycle_profit1 = arbprice - conversion_buy
        cycle_profit2 = arbprice - conversion_sell
        print('Forward profit:', profit)
        print('Forward profit percent:', profit_percent)
        print('Cycle profit1 in currency:', cycle_profit1)
        print('Cycle profit2 in currency:', cycle_profit2)
        if profit > 0:
            print('\nPROFIT!!!!!\n')
        return profit > 0



    def reverseprofit(self, prices1, prices2, straight_conversions, fee, conversion_fee):
        price1, price2 = prices1
        price3, price4 = prices2
        conversion_buy = straight_conversions[0]
        conversion_sell = straight_conversions[1]
        arbprice = (price3 * (1 + fee))/(price2 * (1 - fee))
        profit = conversion_buy - arbprice
        profit_percent = (conversion_buy / arbprice) - 1
        cycle_profit1 = conversion_sell - arbprice
        cycle_profit2 = conversion_buy - arbprice
        print('Reverse profit:', profit)
        print('Reverse profit percent:', profit_percent)
        print('Cycle profit1 in currency:', cycle_profit1)
        print('Cycle profit2 in currency:', cycle_profit2)
        if profit > 0:
            print('\nPROFIT!!!!!\n')
        return profit > 0

    async def loop(self, coin):
        group = self.groups[coin]
        forwardprofit = 0
        forwardloss = 0
        reverseprofit = 0
        reverseloss = 0
        for i in range(len(group)-1):
            for j in range(i+1, len(group)):
                name1 = group[i][-3:] + group[j][-3:]
                name2 = group[j][-3:] + group[i][-3:]
                if (name := name1) in self.keyset or (name := name2) in self.keyset:
                    if name == name2:
                        i, j = j, i
                    fee = self.coins[group[i]].getfee()
                    prices1_task = self.coins[group[i]].getprices()
                    prices2_task = self.coins[group[j]].getprices()
                    straight_conversions_task = self.coins[name].getprices()
                    conversion_fee = self.coins[name].getfee()
                    print('Waiting for prices')
                    prices1, prices2, straight_conversions = await asyncio.gather(
                    prices1_task, prices2_task, straight_conversions_task)
                    print('Prices received')
                    #initial_cost = price1 * (1 + fee) * straight_conversion
                    #selling_profit = price2 * (1 - fee) * (1 - conversion_fee) * initial_cost
                    if not prices1 or not prices2 or not straight_conversions:
                        continue
                    print(name, self.coins[group[i]].getpair(), self.coins[group[j]].getpair(), group[i], group[j])
                    print(prices1, prices2, straight_conversions)
                    forward = self.forwardprofit(prices1, prices2, straight_conversions, fee, conversion_fee)
                    reverse = self.reverseprofit(prices1, prices2, straight_conversions, fee, conversion_fee)
                    forwardprofit += forward
                    forwardloss += not forward
                    reverseprofit += reverse
                    reverseloss += not reverse
        return forwardprofit, forwardloss, reverseprofit, reverseloss

                    
                           




async def main(collector):
    tasks = []
    collector = collector()
    names = collector.coingen()
    collector.grouper()
    forwardprofit = 0
    forwardloss = 0
    reverseprofit = 0
    reverseloss = 0
    for i in collector.groups:
        a, b, c, d = await collector.loop(i)
        forwardprofit += a
        forwardloss += b
        reverseprofit += c
        reverseloss += d
        await asyncio.sleep(2)
    print('Done')
    print(forwardprofit, forwardloss, reverseprofit, reverseloss)
    
if __name__ == '__main__':
    asyncio.run(main(collector))

