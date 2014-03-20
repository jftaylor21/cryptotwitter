import util
import json

class Wallet:
  def __init__(self, cointype, data):
    self.cointype = cointype
    self.address = data['address']
    self.tickerkey = data['tickerkey']
    self.balanceurl = data['balance']
  
  @property
  def balance(self):
    url = self.balanceurl+self.address
    return float(util.readurl(url))

def getWallets(jsonfile):
  ret = {}
  text = util.readurl(jsonfile)
  w = json.loads(text)
  for cointype in w:
    ret[cointype] = Wallet(cointype, w[cointype])
  return ret