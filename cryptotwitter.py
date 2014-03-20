import config.config as config
import lib.twitter
import lib.cryptocurrency.history
import lib.cryptocurrency.util
import lib.cryptocurrency.wallet

import json
import sys
import time
  
def getUSDPerBitcoin():
  text = lib.cryptocurrency.util.readurl(config.TICKER_USD_BTC)
  j = json.loads(text)
  return float(j['last'])
  
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
    
  return lib.cryptocurrency.util.getTimeString()+': $/Bitcoin: '+lib.cryptocurrency.util.delta2str(lib.cryptocurrency.util.usd2str(usdPerBtc), lib.cryptocurrency.util.usd2str(pUsdPerBtc))+' total BTC: '+lib.cryptocurrency.util.delta2str(lib.cryptocurrency.util.coin2str(totalBtc), lib.cryptocurrency.util.coin2str(pTotalBtc))+' total: $'+lib.cryptocurrency.util.delta2str(lib.cryptocurrency.util.usd2str(totalUsd), lib.cryptocurrency.util.usd2str(pTotalUsd))
  
if __name__ == "__main__":
  # we should exit if we can't authenticate with twitter
  try:
    twitter = lib.twitter.Twitter()
  except lib.twitter.AuthenticationError as e:
    print(str(e))
    sys.exit(1)
    
  wallet = lib.cryptocurrency.wallet.getWallets(config.WALLET)
  while(True):
    ticker = lib.cryptocurrency.util.getTicker(config.TICKER)
    usdPerBtc = getUSDPerBitcoin()
    prevhistory = lib.cryptocurrency.history.History(1, config.HISTORY)
    history = lib.cryptocurrency.history.History(1)
    for cointype in wallet:
      btcPerCoin = float(ticker[wallet[cointype].tickerkey])
      h = lib.cryptocurrency.history.HistoryItem(wallet[cointype], btcPerCoin, usdPerBtc)
      history.addHistory(h)
      writeOutputAndSleep(twitter, str(h), config.SLEEP_COIN)
    output = getSummaryOutput(history, prevhistory)
    history.save(config.HISTORY)
    writeOutputAndSleep(twitter, output, config.SLEEP_LOOP)
