import config.config as config
import lib.twitter
import lib.cryptocurrency.history
import lib.cryptocurrency.util

import json
import urllib
import sys
import time

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
  
def delta2str(current, previous):
  delta = float(current)-float(previous)
  deltastr = '{0:+f}'.format(delta).rstrip('.0')
  
  # make sure we didn't strip everything
  if len(deltastr) == 1:
    deltastr = deltastr + '0'
    
  return current+' ('+deltastr+')'
  
def printNextUpdate(secondsToNextUpdate):
  timestr = lib.cryptocurrency.util.getTimeString()+': Next update in '+repr(secondsToNextUpdate)+' seconds'
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
  pTotalUsd = prevhistory.totalInUSD(0)
  
  # average value per bitcoin during this time
  usdPerBtc = 0
  if totalBtc > 0:
    usdPerBtc = totalUsd / totalBtc
  pUsdPerBtc = 0
  if pTotalBtc > 0:
    pUsdPerBtc = pTotalUsd / pTotalBtc
    
  return lib.cryptocurrency.util.getTimeString()+': $/Bitcoin: '+delta2str(lib.cryptocurrency.util.usd2str(usdPerBtc), lib.cryptocurrency.util.usd2str(pUsdPerBtc))+' total BTC: '+delta2str(lib.cryptocurrency.util.coin2str(totalBtc), lib.cryptocurrency.util.coin2str(pTotalBtc))+' total: $'+delta2str(lib.cryptocurrency.util.usd2str(totalUsd), lib.cryptocurrency.util.usd2str(pTotalUsd))
  
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
    prevhistory = lib.cryptocurrency.history.History(1, config.HISTORY)
    history = lib.cryptocurrency.history.History(1)
    for cointype in wallet:
      coindata = wallet[cointype]
      address = coindata['address']
      tickerkey = coindata['tickerkey']
      balance = getBalance(coindata['balance'], address)
      btcPerCoin = float(ticker[tickerkey])
      h = lib.cryptocurrency.history.HistoryItem(cointype, address, tickerkey, balance, btcPerCoin, usdPerBtc)
      history.addHistory(h)
      writeOutputAndSleep(twitter, str(h), config.SLEEP_COIN)
    output = getSummaryOutput(history, prevhistory)
    history.save(config.HISTORY)
    writeOutputAndSleep(twitter, output, config.SLEEP_LOOP)
