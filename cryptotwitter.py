import config

import tweepy
import time
import datetime
import json
import urllib
import cPickle as pickle

class History:
  def __init__(self, cointype, coindata, ticker, usdPerBtc):
    # minimum data needed to calculate other data
    self.cointype = cointype
    self.address = coindata['address']
    self.tickerkey = coindata['tickerkey']
    self.balance = getBalance(coindata['balance'], self.address)
    self.btcPerCoin = float(ticker[self.tickerkey])
    self.usdPerBtc = usdPerBtc
    
    # calculated data
    self.btc = self.balance * self.btcPerCoin
    self.usd = self.btc * self.usdPerBtc
    
  def __str__(self):
    return self.cointype+': '+self.address+' balance: '+repr(self.balance)+' '+self.tickerkey+': '+repr(self.btcPerCoin)+' bitcoin: '+coin2str(self.btc)+ ' $'+usd2str(self.usd)

def readurl(url):
  urlh = urllib.urlopen(url)
  text = urlh.read()
  urlh.close()
  return text

def getPoloniexTicker():
  text = readurl(config.TICKER)
  j = json.loads(text)
  j['BTC_BTC'] = '1' # hack for btc to btc conversions
  return j
  
def getTestTicker():
  text = readurl(config.TICKER_EXAMPLE)
  j = json.loads(text)
  j['BTC_BTC'] = '1' # hack for btc to btc conversions
  return j

def getWallet():
  text = readurl(config.WALLET)
  return json.loads(text)
  
def getTwitterAPI():
  auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
  auth.set_access_token(config.ACCESS_KEY, config.ACCESS_SECRET)
  api = tweepy.API(auth)
  return api
  
def getBalance(baseurl, address):
  url = baseurl+address
  text = readurl(url)
  return float(text)
  
def getUSDPerBitcoin():
  text = readurl(config.TICKER_USD_BTC)
  j = json.loads(text)
  return float(j['last'])

def coin2str(coin):
  return '{0:.8f}'.format(coin)
  
def usd2str(usd):
  return '{0:.2f}'.format(usd)
  
def delta2str(current, previous):
  delta = float(current)-float(previous)
  deltastr = '{0:+f}'.format(delta).rstrip('.0')
  
  # make sure we didn't strip everything
  if len(deltastr) == 1:
    deltastr = deltastr + '0'
    
  return current+' ('+deltastr+')'
  
def printNextUpdate(secondsToNextUpdate):
  t = datetime.datetime.now()
  timestr = t.strftime('%H:%M:%S: Next update in '+repr(secondsToNextUpdate)+' seconds')
  print(timestr)
  
def writeOutputAndSleep(api, output, secondsToNextUpdate):
  if config.TWITTER_OUTPUT:
    api.update_status(output)
  if config.CONSOLE_OUTPUT:
    print(output)
    printNextUpdate(secondsToNextUpdate)
  time.sleep(secondsToNextUpdate)
  
def loadHistory():
  try:
    hfile = open(config.HISTORY, 'rb')
    history = pickle.load(hfile)
    hfile.close()
    return history
  except IOError:
    return []
  
def saveHistory(history):
  hfile = open(config.HISTORY, 'wb')
  pickle.dump(history, hfile)
  hfile.close()
  
def getSummaryOutput(history, prevhistory):
  usdPerBtc = 0
  pUsdPerBtc = 0
  
  totalBtc = 0
  pTotalBtc = 0
  
  totalUsd = 0
  pTotalUsd = 0
  
  for h in history:
    usdPerBtc = h.usdPerBtc
    totalBtc = totalBtc + h.btc
    totalUsd = totalUsd + h.usd
    
  for h in prevhistory:
    pUsdPerBtc = h.usdPerBtc
    pTotalBtc = pTotalBtc + h.btc
    pTotalUsd = pTotalUsd + h.usd
    
  return '$/Bitcoin: '+delta2str(usd2str(usdPerBtc), usd2str(pUsdPerBtc))+' total BTC: '+delta2str(coin2str(totalBtc), coin2str(pTotalBtc))+' total: $'+delta2str(usd2str(totalUsd), usd2str(pTotalUsd))
  
if __name__ == "__main__":
  api = getTwitterAPI()
  wallet = getWallet()
  while(True):
    ticker = getPoloniexTicker()
    usdPerBtc = getUSDPerBitcoin()
    prevhlist = loadHistory()
    hlist = []
    for cointype in wallet:
      h = History(cointype, wallet[cointype], ticker, usdPerBtc)
      hlist.append(h)
      writeOutputAndSleep(api, str(h), config.SLEEP_COIN)
    output = getSummaryOutput(hlist, prevhlist)
    saveHistory(hlist)
    writeOutputAndSleep(api, output, config.SLEEP_LOOP)
