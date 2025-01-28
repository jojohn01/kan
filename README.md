# kan
A project that monitors price discrepancies in Crypto prices in the Kraken trading platform in an attempt to turn a profit through arbitrage

Currently noticed a trend where dicrepancies with different currencies indicated a coming shift in coind prices. Knode2 attmepts to profit off of that. 

The current working arbitrator slowarbitrator. It trades speed for the most up to date information on each coin pair. Does not ouput any foind potential profit at the end of running, as the idea is to integrate it with the simulator file, which still neds to be genralised to handle these new apporaches. (negative dnumbers indicate a loss/no arbitrage oppurtunity at given fee level. Fee level can be changed in the functions. Planned updates to this)

A faster arbitrator is planned that only requests data once, but might be outdated in the tim eit takes to work through everything.

