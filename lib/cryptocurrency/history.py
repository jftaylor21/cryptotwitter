import util

import cPickle as pickle
import collections

class HistoryItem:
  def __init__(self, wallet, btcPerCoin, usdPerBtc):
    # minimum data needed to calculate other data
    self.cointype = wallet.cointype
    self.address = wallet.address
    self.tickerkey = wallet.tickerkey
    self.balance = wallet.balance
    self.btcPerCoin = btcPerCoin
    self.usdPerBtc = usdPerBtc
    
  @property
  def btc(self):
    return self.balance * self.btcPerCoin
  
  @property
  def usd(self):
    return self.btc * self.usdPerBtc
  
  def __str__(self):
    return util.getTimeString()+': '+self.cointype+': '+self.address+' balance: '+str(self.balance)+' '+self.tickerkey+': '+str(self.btcPerCoin)+' bitcoin: '+util.coin2str(self.btc)+ ' $'+util.usd2str(self.usd)
  
  def __sub__(self, other):
    # returns the difference between HistoryItems in a (cointype, difference) tuple
    # cointype will be BTC if the two cointypes are different
    # otherwise cointype will remain the same
    if type(other) is HistoryItem:
      if self.cointype == other.cointype:
        return (self.cointype, self.balance - other.balance)
      else:
        return ('BTC', self.btc - other.btc)
    else:
      raise TypeError('Can\'t subtract '+str(type(other))+' and HistoryItems')

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