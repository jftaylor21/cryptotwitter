import time
import datetime

def getTimeString():
  t = datetime.datetime.now()
  return t.strftime('%H:%M:%S')

def coin2str(coin):
  return '{0:.8f}'.format(coin)
  
def usd2str(usd):
  return '{0:.2f}'.format(usd)