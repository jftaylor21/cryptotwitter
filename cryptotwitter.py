import config

import tweepy
import time
import datetime
import json
import urllib

def readurl(url):
  urlh = urllib.urlopen(url)
  text = urlh.read()
  urlh.close()
  return text

def getPoloniexTicker():
  url = 'https://poloniex.com/public?command=returnTicker'
  text = readurl(url)
  return json.loads(text)
  
def getTestTicker():
  testfile = 'test.txt'
  f = open(testfile, 'r')
  text = f.read()
  f.close()
  return json.loads(text)

def getWallet():
  walletfile = 'wallet.txt'
  f = open(walletfile, 'r')
  text = f.read()
  f.close()
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
  url = 'https://www.bitstamp.net/api/ticker/'
  text = readurl(url)
  j = json.loads(text)
  return float(j['last'])

def coin2str(coin):
  return '{0:.8f}'.format(coin)
  
def usd2str(usd):
  return '{0:.2f}'.format(usd)
  
def printNextUpdate(secondsToNextUpdate):
  t = datetime.datetime.now()
  timestr = t.strftime('%H:%M:%S: Next update in '+repr(secondsToNextUpdate)+' seconds')
  print(timestr)
  
if __name__ == "__main__":
  api = getTwitterAPI()
  wallet = getWallet()
  while(True):
    sleepBetweenUpdates = 60*60*4
    sleepBetweenCoins = 10
    ticker = getPoloniexTicker()
    ticker['BTC_BTC'] = '1'
    usdPerBitcoin = getUSDPerBitcoin()
    total = 0
    for cointype in wallet:
      address = wallet[cointype]['address']
      tickerkey = wallet[cointype]['tickerkey']
      balance = getBalance(wallet[cointype]['balance'], address)
      bitcoin = float(ticker[tickerkey])
      totalBitcoin = balance * bitcoin
      total = total + totalBitcoin
      usd = usdPerBitcoin * totalBitcoin
      output = cointype+': '+address+' balance: '+repr(balance)+' '+tickerkey+': '+repr(bitcoin)+' bitcoin: '+coin2str(totalBitcoin)+ ' $'+usd2str(usd)
      print(output)
      api.update_status(output)
      printNextUpdate(sleepBetweenCoins)
      time.sleep(sleepBetweenCoins)
    output = '$/Bitcoin: '+repr(usdPerBitcoin)+' total wallets (bitcoins): '+coin2str(total)+' total $'+usd2str(total*usdPerBitcoin)
    print(output)
    api.update_status(output)
    printNextUpdate(sleepBetweenUpdates)
    time.sleep(sleepBetweenUpdates)