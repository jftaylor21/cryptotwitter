import tweepy
import config.twitter

MAX_MESSAGE_SIZE = 140

# exceptions
class TwitterError(Exception):
  def __init__(self, msg):
    self.msg = msg
    
  def __str__(self):
    return self.msg

class AuthenticationError(TwitterError):
  def __init__(self):
    super(AuthenticationError, self).__init__('Authentication values in config/twitter.py are not valid')
    
class CharacterLimitError(TwitterError):
  def __init__(self, numCharacters):
    super(CharacterLimitError, self).__init__('Tried to post message of size '+str(numCharacters)+' when limit is '+str(MAX_MESSAGE_SIZE)+' characters')

# actual twitter class
class Twitter:
  def __init__(self):
    auth = tweepy.OAuthHandler(config.twitter.CONSUMER_KEY, config.twitter.CONSUMER_SECRET)
    auth.set_access_token(config.twitter.ACCESS_KEY, config.twitter.ACCESS_SECRET)
    self.api = tweepy.API(auth)
    
    if not self.api.verify_credentials():
      raise AuthenticationError()
  
  def tweet(self, message):
    if len(message) > MAX_MESSAGE_SIZE:
      raise CharacterLimitError(len(message))
      
    try:
      self.api.update_status(message)
    except tweepy.TweepError as e:
      raise TwitterError(str(e))