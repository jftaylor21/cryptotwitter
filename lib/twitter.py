import tweepy
import config.twitter

class Twitter:
  def __init__(self):
    auth = tweepy.OAuthHandler(config.twitter.CONSUMER_KEY, config.twitter.CONSUMER_SECRET)
    auth.set_access_token(config.twitter.ACCESS_KEY, config.twitter.ACCESS_SECRET)
    self.api = tweepy.API(auth)
  
  def tweet(self, message):
    try:
      self.api.update_status(message)
    except TweepError, e:
      pass