
class coordinator:

    def __init__(self):

        self.converters = {}
        self.order = ['ETH', 'XBT', 'EUR', 'GBP', 'AUD', 'USD', 'JPY' ]
        self.coinsrecieved = set()
        self.currentcoin = None
        self.previouscoin = None
        self.coininfo = {}
        self.activesesh = []
        self.exclude = set()
    
    def callconv(self, converter):
        converter.point(self)
        answer = converter.giveself()
        self.converters[answer[0]] = answer[1]

    def coincall(self, coinnode):
        coinnode.point(self)

    def cointake(self, info):
        if info[0] not in self.coinsrecieved and info != None:
            if len(self.activesesh) > 1:
                self.coincompare()
            self.previouscoin = info[0]
            self.activesesh.clear()
            self.coinsrecieved.add(info[0])
        self.activesesh.append(info[1:])
        if info == None:
            self.coincompare()
            self.activesesh.clear()


    def coincompare(self):
        count = len(self.activesesh)-1
        for i in range(count):
            currency1 = self.activesesh[i][1]
            comp = i + 1
            for j in range(count):
                currency2 = self.activesesh[j+comp][1]   
                ex_check = currency1+currency2
                if ex_check not in self.exclude:
                    pair = self.currencycompare(currency1, currency2)
                    converter = self.converters[pair]
                    if pair[:3] == currency1:              
                        price = float(self.activesesh[i][0])
                        bottom = float(self.activesesh[j+comp][0])
                    else:
                        price = float(self.activesesh[j+comp][0])
                        bottom = float(self.activesesh[i][0])
                    expected = converter.expected(price)
                    percent = 100 * (1 - (expected/bottom))
                    if percent > 0.52 or percent < -0.52:
                        print(self.previouscoin, str(price)+pair[:3], str(bottom)+pair[3:], str(percent)+'%'+' difference')
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
        


class converter:

    def __init__(self, currency, conversions, fees):
        
        self.fees = fees
        self.currency = currency
        self.conversion = conversions
        self.coordinator = None


    def expected(self, price):
        expected = float(price) * float(self.conversion)
        return expected

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

    def __init__(self, price, pair, fees):

        self.pair = pair
        self.fees = fees
        self.price = price
        self.coin = pair[0:len(pair)-3]
        self.currency = pair[len(pair)-3:len(pair)]
        self.coordinator = None
        self.tester = None


    def point(self, coordinator):
        self.coordinator = coordinator

    def sendinfo(self):
        info  = [self.coin, self.price, self.currency, self.fees]
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
        print(self.price)

    def getpair(self):
        print(self.pair)
        return self.pair


class tester:

    def __init__(self):
        
        self.currency1ab = None
        self.currency2ab = None

    def test(self):
        pass


    def getcoininfo(self, info):
        coin1 = info[0] + info[1]




def main():
    print('test')
    test_coins = [[{'1INCHEUR': '1.218'}, {'1INCHUSD': '1.380'}], [{'AAVEAUD': '178.54'}], [{'AAVEETH': '0.0517'}], [{'AAVEEUR': '116.35'}], [{'AAVEGBP': '95.26'}], [{'AAVEUSD': '132.07'}], [{'AAVEXBT': '0.003553'}], [{'ACAEUR': '0.954'}], [{'ACAUSD': '1.051'}], [{'ADAAUD': '1.17784'}], [{'ADAETH': '0.0003326'}], [{'ADAEUR': '0.747522'}], [{'ADAGBP': '0.62145'}], [{'ADAUSD': '0.845722'}], [{'ADAXBT': '0.00002279'}], [{'AIREUR': '0.0619'}], [{'AIRUSD': '0.0706'}], [{'AKTEUR': '1.0874'}], [{'AKTUSD': '1.2100'}], [{'ALGOETH': '0.0003061'}], [{'ALGOEUR': '0.69205'}], [{'ALGOGBP': '0.57400'}], [{'ALGOUSD': '0.78453'}], [{'ALGOXBT': '0.00002107'}], [{'ANKREUR': '0.05287'}], [{'ANKRGBP': '0.04350'}], [{'ANKRUSD': '0.05983'}], [{'ANKRXBT': '0.00000161'}], [{'ANTETH': '0.001821'}], [{'ANTEUR': '4.0957'}]]
    unpacker = []
    for i in test_coins:
        unpacker.extend(i)
    for i in unpacker:
        pass
