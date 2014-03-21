import time
import datetime
import urllib
import json

# time related
def getTimeString():
  t = datetime.datetime.now()
  return t.strftime('%H:%M:%S')

# conversions to string
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

# url related
def readurl(url):
  # need to add check for errors
  text = ''
  try:
    urlh = urllib.urlopen(url)
    text = urlh.read()
    urlh.close()
  except IOErrror as e:
    pass
  return text
  
# ticker related
def getTicker(url):
  text = readurl(url)
  j = json.loads(text)
  j['BTC_BTC'] = '1' # hack for btc to btc conversions
  return j