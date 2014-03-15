#Installation
###Dependencies
* [Python 2.6](http://www.python.org/)
* [Tweepy](https://github.com/tweepy/tweepy)
* [Git](http://git-scm.com/)

###Steps
1. git clone https://github.com/jftaylor21/cryptotwitter.git
1. Copy config/config-template.py to config/config.py and modify it for your environment
1. Copy config/twitter-template.py to config/twitter.py and modify it for your environment
1. Copy config/wallet-template.json to config/wallet.json and add your coins to it
1. Run cryptotwitter.py

#Wallet Configuration
The wallet is in JSON format. 

Example:
````JSON
"redd":
{
  "address":"Rw2k4Vsf4ckvBktkpCPMrdrx423syUjeMb",
  "tickerkey":"BTC_REDD",
  "balance":"http://cryptexplorer.com/chain/reddcoin/q/addressbalance/"
}
````

"redd" is the coinname. This can be whatever you want.

"address" is the public address for your wallet.

"tickerkey" corresponds to the ticker conversion to bitcoin from config.py.

"balance" is the url to get the current wallet balance. The "address" will be concatenated to the end of it.