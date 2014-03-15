# wallet
# contains all public coin addresses
# see README.md and wallet-example.json
WALLET = 'config/wallet.json'

# ticker
# contains all coin conversions
TICKER_EXAMPLE = 'data/ticker-example.json'
TICKER = 'https://poloniex.com/public?command=returnTicker'
TICKER_USD_BTC = 'https://www.bitstamp.net/api/ticker/'

# sleep in seconds
SLEEP_LOOP = 60*60*4
SLEEP_COIN = 10

# output options
CONSOLE_OUTPUT = True
TWITTER_OUTPUT = True

# history files to calculate difference between now and previous update
HISTORY = 'data/history.pkl'
