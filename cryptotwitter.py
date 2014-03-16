import config.config as config
import lib.twitter

import time
import datetime
import json
import urllib
import cPickle as pickle
import sys
import collections

class HistoryItem:
  def __init__(self, cointype, coindata, ticker, usdPerBtc):
    # minimum data needed to calculate other data
    self.cointype = cointype
    self.address = coindata['address']
    self.tickerkey = coindata['tickerkey']
    self.balance = getBalance(coindata['balance'], self.address)
    self.btcPerCoin = float(ticker[self.tickerkey])
    self.usdPerBtc = usdPerBtc
    
  @property
  def btc(self):
    return self.balance * self.btcPerCoin
  
  @property
  def usd(self):
    return self.btc * self.usdPerBtc
  
  def __str__(self):
    return getTimeString()+': '+self.cointype+': '+self.address+' balance: '+repr(self.balance)+' '+self.tickerkey+': '+repr(self.btcPerCoin)+' bitcoin: '+coin2str(self.btc)+ ' $'+usd2str(self.usd)

class History:
  '''Keeps numEntries of history for each coin type'''
  def __init__(self, numEntries, filename=None):
    self.numEntries = numEntries
    self.load(filename)
    
  def addHistory(self, item):
    # Can only add one item at a time.
    # maxlen of the deque will remove old entries automatically
    self._history.setdefault(item.cointype, collections.deque(maxlen=self.numEntries))
    self._history[item.cointype].append(item)
    
  def load(self, filename):
    # load will clear current history and load history from file.
    # no errors will occur if opening the file fails. This is assumed to be the
    # case where it is the first time the program is run and there is no
    # history.
    self._history = {}
    if filename is not None:
      try:
        hfile = open(filename, 'rb')
        self._history = pickle.load(hfile)
        hfile.close()
      except IOError:
        pass
      
  def save(self, filename):
    hfile = open(filename, 'wb')
    pickle.dump(self._history, hfile)
    hfile.close()
  
  def totalInBTC(self, entry):
    # entry 0 is most current
    total = 0
    for cointype in self._history:
      historylen = len(self._history[cointype])
      index = historylen-entry-1
      if index >= 0 and index < historylen:
        total = total + self._history[cointype][index].btc
      else: # should there be an error here?
        print('Index '+str(index)+' out of valid ranges of 0-'+str(historylen))
    return total
    
  def totalInUSD(self, entry):
    # entry 0 is most current
    total = 0
    for cointype in self._history:
      historylen = len(self._history[cointype])
      index = historylen-entry-1
      if index >= 0 and index < historylen:
        total = total + self._history[cointype][index].usd
      else: # should there be an error here?
        print('Index '+str(index)+' out of valid ranges of 0-'+str(historylen))
    return total

def readurl(url):
  # need to add check for errors
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
  
def getSummaryOutput(history, prevhistory):
  totalBtc = history.totalInBTC(0)
  pTotalBtc = prevhistory.totalInBTC(0)
  
  totalUsd = history.totalInUSD(0)
  pTotalUsd = history.totalInUSD(0)
  
  # average value per bitcoin during this time
  usdPerBtc = 0
  if totalBtc > 0:
    usdPerBtc = totalUsd / totalBtc
  pUsdPerBtc = 0
  if pTotalBtc > 0:
    pUsdPerBtc = pTotalUsd / pTotalBtc
    
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
    prevhistory = History(1, config.HISTORY)
    history = History(1)
    for cointype in wallet:
      h = HistoryItem(cointype, wallet[cointype], ticker, usdPerBtc)
      history.addHistory(h)
      writeOutputAndSleep(twitter, str(h), config.SLEEP_COIN)
    output = getSummaryOutput(history, prevhistory)
    history.save(config.HISTORY)
    writeOutputAndSleep(twitter, output, config.SLEEP_LOOP)
