import time, requests


def fiatfilter(name):
    return len(name) <= 4 and (('USD' in name and name.endswith('USD')) or 'USD' not in name) and name != 'WETH'

class infoorganizer:

    def __init__(self):
        self.currencies = set()
        self.special = set(['XBT, ETH'])
        self.alts = set()
        self.fiats = {}
        self.fiatpairs = set()
        self.assets = None
        self.pairs = None
        self.groups = {}
        self.atoalts = {}
        pass


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

    def getassets(self):
        assets = requests.get('https://api.kraken.com/0/public/Assets?')
        assets = assets.json()
        assets = assets['result']
        self.assets = assets
        for i in assets:
            self.alts.add(assets[i]['altname'])
        pairs = requests.get('https://api.kraken.com/0/public/AssetPairs?')
        pairs = pairs.json()
        pairs = pairs['result']
        self.pairs = pairs
        for i in assets:
            names = [i, assets[i]['altname']]
            self.atoalts[i] = assets[i]['altname']
            for j in names:
                for k in pairs:
                    pairnames = [k, pairs[k]['altname']]
                    for l in pairnames:
                        if l.endswith(j):
                            if l[:-len(j)] in assets or l[:-len(j)] in self.alts:
                                self.currencies.add(j)
                                self.fiats[i] = assets[i]['altname']
                                self.fiats[assets[i]['altname']] = i
        self.currencies = set(filter(fiatfilter, self.currencies))
        print(self.currencies)
        print('done')

    
    def pairfiats(self):
        for i in self.currencies:
            for j in self.currencies:
                if i+j in self.pairs:
                    self.fiatpairs.add(i+j)
        print(self.fiatpairs)
    
    def checkassets(self):
        paired = set()
        for i in self.currencies:
            for j in self.pairs:
                if j.endswith(i) and j[:-len(i)] in self.assets:
                    print("{} is paired with {}".format(j[:-len(i)], i))
                    self.groups[j:-len(i)] = self.groups.get(j[:-len(i)], []).append(i)
                    paired.add(j[:-len(i)])
        for i in self.atoalts:
            if i not in paired and self.atoalts[i] not in paired:
                print("{} is not paired with anything".format(i))



test = infoorganizer()
test.getassets()
test.pairfiats()
test.checkassets()