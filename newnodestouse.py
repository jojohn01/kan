
from simulator import tradesimulator

class coordinator:

    def __init__(self, exclude = set()):

        self.converters = {}
        self.order = ['ETH', 'XBT', 'EUR', 'GBP', 'AUD', 'USD', 'JPY' ]
        self.coinsrecieved = set()
        self.currentcoin = []
        self.previouscoin = None
        self.coininfo = {}
        self.activesesh = []
        self.exclude = exclude
        self.hitcounter = 0
        self.etherium = 0
        self.bitcoin = 0
        self.simulator = None
    
    def callconv(self, converter):
        converter.point(self)
        answer = converter.giveself()
        self.converters[answer[0]] = answer[1]

    def coincall(self, coinnode):
        coinnode.point(self)

    def cointake(self, info):
        if info != None and info[0] not in self.coinsrecieved:
            self.currentcoin.append(info[0])
            if len(self.activesesh) > 1:
                self.coincompare()
            self.previouscoin = info[0]
            self.activesesh.clear()
            self.coinsrecieved.add(info[0])
        if info != None:
            self.activesesh.append(info[1:])
        if info == None:
            self.coincompare()
            self.activesesh.clear()


    def coincompare(self):
        count = len(self.activesesh)-1
        for i in range(count):
            currency1 = self.activesesh[i][2]
            comp = i + 1
            for j in range(count):
                currency2 = self.activesesh[j+comp][2]
                ex_check = currency1+currency2
                if ex_check not in self.exclude:
                    pair = self.currencycompare(currency1, currency2)
                    converter = self.converters[pair]
                    if pair[:3] == currency1:              
                        price = [float(self.activesesh[i][0]), float(self.activesesh[i][1])]
                        bottom = [float(self.activesesh[j+comp][0]), float(self.activesesh[j+comp][1])]
                    else:
                        price = [float(self.activesesh[j+comp][0]), float(self.activesesh[j+comp][1])]
                        bottom = [float(self.activesesh[i][0]), float(self.activesesh[i][1])]
                    expected = converter.expected(price, bottom)
                    if expected[0] > 0:
                        print(self.previouscoin, str(expected[1])+str(expected[3][:3]), str(expected[2])+str(expected[3][3:]), str(expected[0])+str(expected[3][3:]), ' Profit')
                        self.hitcounter = self.hitcounter + 1
                        if str(expected[3][:3]) == 'ETH':
                            self.etherium = self.etherium + 1
                        elif str(expected[3][:3]) == 'XBT':
                            self.bitcoin = self.bitcoin + 1
            count = count - 1
            



    def currencycompare(self, currency1, currency2):
        c1_index = self.order.index(currency1)
        c2_index = self.order.index(currency2)
        if c1_index < c2_index:
            cur_pair = currency1 + currency2
        else:
            cur_pair = currency2 + currency1
        return cur_pair


    def convertercheck(self):
        print('Connected to these converters', self.converters)
        

    def hitstatus(self):
        if self.hitcounter == 0:
            print("No hits :(")
        else:
            print('{} hits!'.format(self.hitcounter))

    def getsimulator(self, simulator):
        self.simulator = simulator

    def tradecheck(self):
        self.simulator.action([self.etherium, self.bitcoin])

    def reset(self):
        self.converters = {}
        self.order = ['ETH', 'XBT', 'EUR', 'GBP', 'AUD', 'USD', 'JPY' ]
        self.coinsrecieved = set()
        self.currentcoin = []
        self.previouscoin = None
        self.coininfo = {}
        self.activesesh = []
        self.exclude = set()
        self.hitcounter = 0
        self.etherium = 0
        self.bitcoin = 0




class converter:

    def __init__(self, currency, conversions, fees):
        
        self.fees = fees
        self.currency = currency
        self.conversion = conversions
        self.coordinator = None


    def expected(self, price, bottom):
        checkone = [x for x in price if x]
        checktwo = [x for x in bottom if x]
        if not checkone or not checktwo:
            return [0, None, None, None]
        conv_price = float(price[0]) * float(self.conversion)
        base_sell = float(bottom[1])
        fee = (0.0026 * conv_price) + (0.0026 * base_sell)
        difference = base_sell - conv_price
        direction = None
        buy = None
        if difference > fee:
            print('HIT')
            direction = self.currency
            buy = price[0]
        else:
            conv_price = float(bottom[0])/float(self.conversion)
            base_sell = float(price[1])
            fee = (0.001 * conv_price) + (0.001 * base_sell)
            difference = base_sell - conv_price
            if difference > fee:
                print('HIT Flip!')
                direction = self.currency[3:] + self.currency[:3]
                buy = bottom[0]
        return [difference - fee, buy, base_sell, direction]

    def point(self, coordinator):
        self.coordinator = coordinator

    def giveself(self):
        answer = [self.currency, self]
        return answer

    def connectcheck(self):
        if self.coordinator:
            print("Converter connected to", self.coordinator)
        else:
            print("Not connected")



class pricenode:

    def __init__(self, pair, ask, best, fees):

        self.pair = pair
        self.fees = fees
        self.ask = ask
        self.best = best
        self.coin = pair[0:len(pair)-3]
        self.currency = pair[len(pair)-3:len(pair)]
        self.coordinator = None
        self.tester = None


    def point(self, coordinator):
        self.coordinator = coordinator

    def sendinfo(self):
        info  = [self.coin, self.ask, self.best, self.currency, self.fees]
        if self.coordinator:
            self.coordinator.cointake(info)
        else:
            print('No coordinator :(')


    def connectcheck(self):
        if self.coordinator:
            print("Coin connected to", self.coordinator)
        else:
            print("Not connected")

    def getprice(self):
        print(self.ask, self.best)

    def getpair(self):
        print(self.pair)
        return self.pair


class Aconverter(converter):

    def expected(self, price, bottom):
        conv_price = float(price[0]) * float(self.conversion)
        base_sell = float(bottom[1])
        fee = (0.0026 * conv_price) + (0.0026 * base_sell)
        difference = base_sell - conv_price
        direction = None
        buy = None
        if abs(difference) > fee:
            print('HIT')
            if difference > 0:
                direction = self.currency
                buy = price[0]
            else:
                direction = self.currency[3:] + self.currency[:3]
                buy = bottom[0]
                base_sell = float(price[1])
        return [abs(difference) - fee, buy, base_sell, direction]

class Acoordinator(coordinator):

    def __init__(self, exclude = set()):
        super().__init__(exclude)


    def coincompare(self):
        count = len(self.activesesh)-1
        for i in range(count):
            currency1 = self.activesesh[i][2]
            comp = i + 1
            for j in range(count):
                currency2 = self.activesesh[j+comp][2]
                ex_check = currency1+currency2
                if ex_check not in self.exclude:
                    pair = self.currencycompare(currency1, currency2)
                    converter = self.converters[pair]
                    if pair[:3] == currency1:              
                        price = [float(self.activesesh[i][0]), float(self.activesesh[i][1])]
                        bottom = [float(self.activesesh[j+comp][0]), float(self.activesesh[j+comp][1])]
                    else:
                        price = [float(self.activesesh[j+comp][0]), float(self.activesesh[j+comp][1])]
                        bottom = [float(self.activesesh[i][0]), float(self.activesesh[i][1])]
                    expected = converter.expected(price, bottom)
                    if expected[0] > 0:
                        print(self.previouscoin, str(expected[1])+str(expected[3][:3]), str(expected[2])+str(expected[3][3:]), str(expected[0])+str(expected[3][3:]), ' Profit')
                        self.simulator.action(self.previouscoin, expected[3][:3], expected[3][3:])
                        pass