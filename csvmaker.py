from newdatacollector import Training_data_collector
import pandas as pd
import threading
import pickle

class csvmaker:
    
    def __init__(self, target, intervals = [1, 3, 5, 15, 30]):
        #Creates a series of dataframes for each interval of time for the target coin 
        self.coins = target
        self.intervals = intervals
        self.data = Training_data_collector(target, intervals)
        threads = [threading.Thread(target=self.__make_csv), threading.Thread(target=self.__make_pickle)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    
    def __make_csv(self):
        #Creates a csv file for each interval of time for the target coin
        threads = []
        for i in self.intervals:
            newframe = None
            for coin in self.coins:
                self.data.getPriceData()[coin]['{} minute interval'.format(i)]['coin name'] = coin
                if newframe is None:
                    newframe = self.data.getPriceData()[coin]['{} minute interval'.format(i)]
                else:
                    newframe = pd.concat([newframe, self.data.getPriceData()[coin]['{} minute interval'.format(i)]])
            thread= threading.Thread(target=newframe.to_csv,  args=('../kmardata_{}_minute.csv'.format(i),), kwargs={'index': False})
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

    def __make_pickle(self):
        #Creates a pickle file for each interval of time for the target coin
        threads = []
        for i in self.intervals:
            newframe = {}
            for coin in self.coins:
                 newframe[coin] = self.data.getPriceData()[coin]['{} minute interval'.format(i)]
            labels, frames = zip(*newframe.items())
            finalframe = pd.concat(frames, keys=labels, axis=1)
            thread = threading.Thread(target=finalframe.to_pickle, args=('../kmardata_{}_minute.pkl'.format(i),))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        
        
            
if __name__ == '__main__':
    coins = ['XBT', 'ETH', 'MORPHO', 'ADA', 'XRP', 'SOL', 'PEPE', 'DOGE', 'DRIFT', 'PONKE', 'BONK']
    csvmaker(coins)

