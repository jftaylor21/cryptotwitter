import config.config as config
import lib.twitter

import time
import datetime
import json
import urllib
import cPickle as pickle
import sys

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
    return getTimeString()+': '+self.cointype+': '+self.address+' balance: '+repr(self.balance)+' '+self.tickerkey+': '+repr(self.btcPerCoin)+' bitcoin: '+coin2str(self.btc)+ ' $'+usd2str(self.usd)

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
  
def getTimeString():
  t = datetime.datetime.now()
  return t.strftime('%H:%M:%S')
  
def printNextUpdate(secondsToNextUpdate):
  timestr = getTimeString()+': Next update in '+repr(secondsToNextUpdate)+' seconds'
  print(timestr)
  
def writeOutputAndSleep(twitter, output, secondsToNextUpdate):
  if config.TWITTER_OUTPUT:
    try:
      twitter.tweet(output)
    except TwitterError as e:
      print(str(e))
      
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
    
  return getTimeString()+': $/Bitcoin: '+delta2str(usd2str(usdPerBtc), usd2str(pUsdPerBtc))+' total BTC: '+delta2str(coin2str(totalBtc), coin2str(pTotalBtc))+' total: $'+delta2str(usd2str(totalUsd), usd2str(pTotalUsd))
  
if __name__ == "__main__":
  # we should exit if we can't authenticate with twitter
  try:
    twitter = lib.twitter.Twitter()
  except lib.twitter.AuthenticationError as e:
    print(str(e))
    sys.exit(1)
    
  wallet = getWallet()
  while(True):
    ticker = getPoloniexTicker()
    usdPerBtc = getUSDPerBitcoin()
    prevhlist = loadHistory()
    hlist = []
    for cointype in wallet:
      h = History(cointype, wallet[cointype], ticker, usdPerBtc)
      hlist.append(h)
      writeOutputAndSleep(twitter, str(h), config.SLEEP_COIN)
    output = getSummaryOutput(hlist, prevhlist)
    saveHistory(hlist)
    writeOutputAndSleep(twitter, output, config.SLEEP_LOOP)
