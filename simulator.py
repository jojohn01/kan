import requests

class tradesimulator():
    

    def __init__(self):

        self.buyprice = None
        self.sellprice = None
        self.buynumber = 0
        self.bought = False
        self.sellnumber = 0
        self.profit = 0
        self.streak = 0

    def action(self, hits):
        self.buynumber = hits[0]  + hits[1]
        if self.bought == False:
            self.buydecide()
        else:
            self.selldecide()
   
    def buydecide(self):
        if self.buynumber > 3:
            self.streak = self.streak + 1
        else:
            self.streak = 0
        if self.streak >= 2 and not self.bought:
            self.bought = True
            self.streak = 0
            self.buy()
        else:
            print('Did not buy')

    def selldecide(self):
        if self.buynumber < 3 and self.bought:
            self.streak = self.streak + 1
        else:
            self.streak = 0
        if self.streak <= 2 and self.bought:
            self.streak = 0
            self.bought = False
            self.sell()
        else:
            print('Did not sell')




    def buy(self):
        price = requests.get('https://api.kraken.com/0/public/Ticker?pair=ETHUSD')
        price = price.json()
        price = price['result']
        price = price['XETHZUSD']
        price = price['a'][0]
        self.buyprice = price
        self.buynumber = 0
        print('Bought at', price)

    def sell(self):
        price = requests.get('https://api.kraken.com/0/public/Ticker?pair=ETHUSD')
        price = price.json()
        price = price['result']
        price = price['XETHZUSD']
        price = price['b'][0]
        self.sellprice = price
        self.sellnumber = 0
        print('Sold at', price)
        self.profitcalc()

    def profitcalc(self):
        self.profit = ((float(self.sellprice) / float(self.buyprice)) - 1)
        if self.profit > 0:
            print('Profit', self.profit, '%')
        else:
            print('Loss', abs(self.profit), '%')
        self.filesave()
        self.reset()
    
        
    def filesave(self):
        record = open('Test_history', 'a')
        record.write(str(self.profit) + '%'+'\n')
        record.close()

    def reset(self):
        self.buyprice = None
        self.sellprice = None
        self.buynumber = 0
        self.bought = False
        self.sellnumber = 0


