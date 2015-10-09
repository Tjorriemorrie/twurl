from src import app
from google.appengine.ext import ndb
import datetime


class User(ndb.Model):
    email = ndb.StringProperty(required=True)
    topics = ndb.StringProperty(repeated=True)

    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)

    @staticmethod
    def fetchByTopic(topic):
        users = User.query(User.topics == topic).fetch()
        app.logger.info('Fetched {} users for topic {}'.format(len(users), topic))
        return users


class Tweet(ndb.Model):
    id = ndb.StringProperty(required=True)
    text = ndb.StringProperty(required=True)
    tweeted_at = ndb.DateTimeProperty(required=True)
    retweet_count = ndb.IntegerProperty(required=True, default=0)
    favorite_count = ndb.IntegerProperty(required=True, default=0)

    user_id = ndb.StringProperty(required=True)
    user_screen_name = ndb.StringProperty(required=True)
    user_profile_img = ndb.StringProperty(required=True)
    user_friends_count = ndb.IntegerProperty(required=True)
    user_followers_count = ndb.IntegerProperty(required=True)

    urls = ndb.StringProperty(repeated=True)

    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)

    @staticmethod
    def create(topic, tweet_info):
        args = {
            'id': tweet_info['id_str'],
            'text': tweet_info['text'],
            'tweeted_at': datetime.datetime.strptime(tweet_info['created_at'], '%a %b %d %H:%M:%S +0000 %Y'),
            'retweet_count': tweet_info['retweet_count'],
            'favorite_count': tweet_info['favorite_count'],
    
            'user_id': tweet_info['user']['id_str'],
            'user_screen_name': tweet_info['user']['screen_name'],
            'user_profile_img': tweet_info['user']['profile_background_image_url'],
            'user_friends_count': tweet_info['user']['friends_count'],
            'user_followers_count': tweet_info['user']['followers_count'],
    
            'urls': [url['expanded_url'] for url in tweet_info['entities']['urls']],
        }
        tweet = Tweet.get_or_insert(tweet_info['id_str'], parent=ndb.Key('Topic', topic), **args)
        app.logger.debug('Tweet: {}'.format(tweet))
        return tweet

    @staticmethod
    def fetchByTopic(topic):
        tweets = Tweet.query(ancestor=ndb.Key('Topic', topic)).fetch()
        app.logger.info('Fetched {} tweets by {}'.format(len(tweets), topic))
        return tweets

    @staticmethod
    def since_id(topic):
        last_tweet = Tweet.query(
            ancestor=ndb.Key('Topic', topic),
            projection=[Tweet.id]
        ).order(-Tweet.id).get()
        if not last_tweet:
            since_id = 0
        else:
            since_id = last_tweet.id
        app.logger.info('Since id for topic {} is {}'.format(topic, since_id))
        return since_id

    @staticmethod
    @ndb.transactional
    def removeOld(time_ago, topic):
        app.logger.info('Remove old tweets before {}'.format(time_ago))

        tweet_keys = Tweet.query(Tweet.updated_at < time_ago, ancestor=ndb.Key('Topic', topic)).fetch(keys_only=True)
        for tweet_key in tweet_keys:
            app.logger.debug('Removing tweet {}'.format(tweet_key))
            tweet_key.delete()

        app.logger.info('Removed {} tweets for {}'.format(len(tweet_keys), topic))


# {u'in_reply_to_status_id': None,
#  u'user': {
#      u'protected': False,
#      u'screen_name': u'EvanPeterWill',
#      u'verified': False,
#      u'default_profile': True,
#      u'statuses_count': 60,
#      u'profile_background_color': u'C0DEED',
#      u'following': None,
#      u'notifications': None,
#      u'friends_count': 65,
#      u'profile_sidebar_border_color': u'C0DEED',
#      u'url': None,
#      u'follow_request_sent': None,
#      u'utc_offset': -25200,
#      u'profile_text_color': u'333333',
#      u'profile_link_color': u'0084B4',
#      u'time_zone': u'Pacific Time (US & Canada)',
#      u'contributors_enabled': False,
#      u'favourites_count': 21,
#      u'listed_count': 1,
#      u'profile_background_image_url_https': u'https://abs.twimg.com/images/themes/theme1/bg.png',
#      u'profile_image_url_https': u'https://pbs.twimg.com/profile_images/632289574429962240/Rtez7C3H_normal.jpg',
#      u'description': u'Digital Librarian',
#      u'id': 3315299046,
#      u'has_extended_profile': False,
#      u'geo_enabled': False,
#      u'is_translator': False,
#      u'followers_count': 19,
#      u'created_at': u'Fri Aug 14 20:08:43 +0000 2015',
#      u'location': u'Moscow, ID',
#      u'profile_image_url': u'http://pbs.twimg.com/profile_images/632289574429962240/Rtez7C3H_normal.jpg',
#      u'id_str': u'3315299046',
#      u'is_translation_enabled': False,
#      u'profile_sidebar_fill_color': u'DDEEF6',
#      u'profile_background_tile': False,
#      u'lang': u'en',
#      u'profile_background_image_url': u'http://abs.twimg.com/images/themes/theme1/bg.png',
#      u'entities': {u'description': {u'urls': []}}, u'default_profile_image': False,
#      u'name': u'Evan Williamson',
#      u'profile_use_background_image': True
#     },
#  u'favorited': False,
#  u'in_reply_to_user_id': None,
#  u'retweeted': False,
#  u'coordinates': None,
#  u'geo': None,
#  u'metadata': {u'iso_language_code': u'en', u'result_type': u'recent'},
#  u'possibly_sensitive': False,
#  u'source': u'<a href="http://twitter.com" rel="nofollow">Twitter Web Client</a>',
#  u'in_reply_to_status_id_str': None,
#  u'in_reply_to_screen_name': None,
#  u'id': 651454457658523648,
#  u'in_reply_to_user_id_str': None,
#  u'created_at': u'Tue Oct 06 17:50:20 +0000 2015',
#  u'text': u'looking at #python thinking: import this https://t.co/G2J32KGWgy', u'truncated': False,
#  u'id_str': u'651454457658523648',
#  u'lang': u'en',
#  u'entities': {
#      u'hashtags': [
#          {
#              u'text': u'python',
#              u'indices': [11, 18]
#          }
#      ],
#      u'user_mentions': [],
#      u'urls': [
#         {
#             u'display_url': u'python.org/dev/peps/pep-0\u2026',
#             u'indices': [41, 64],
#             u'expanded_url': u'https://www.python.org/dev/peps/pep-0020/',
#             u'url': u'https://t.co/G2J32KGWgy'
#         }
#      ],
#         u'symbols': []},
#  u'place': None,
#  u'favorite_count': 0,
#  u'retweet_count': 0,
#  u'is_quote_status': False,
#  u'contributors': None
#  }

class Link(ndb.Model):
    id = ndb.StringProperty(required=True)
    tweeted_count = ndb.IntegerProperty(required=True)
    retweeted_sum = ndb.FloatProperty(required=True)
    favorite_sum = ndb.FloatProperty(required=True)
    priority = ndb.ComputedProperty(lambda self: self.tweeted_count + self.retweeted_sum + self.favorite_sum)

    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)

    @staticmethod
    def create(topic, url, url_info):
        link = Link.get_or_insert(url, parent=ndb.Key('Topic', topic), **url_info)
        if link.tweeted_count != url_info['tweeted_count']:
            link.populate(**url_info)
            link.put()
        app.logger.debug('Link: {}'.format(link))
        return link

    @staticmethod
    def fetchByTopic(topic):
        links = Link.query(ancestor=ndb.Key('Topic', topic)).order(-Link.priority).fetch()
        app.logger.info('Fetched {} links for topic {}'.format(len(links), topic))
        return links

    @staticmethod
    @ndb.transactional
    def removeOld(topic, time_ago):
        app.logger.info('Remove old links before {}'.format(time_ago))

        link_keys = Link.query(Link.updated_at < time_ago, ancestor=ndb.Key('Topic', topic)).fetch(keys_only=True)
        for link_key in link_keys:
            app.logger.debug('Removing link {}'.format(link_key))
            link_key.delete()

        app.logger.info('Removed {} links for {}'.format(len(link_keys), topic))


class UserLink(ndb.Model):
    user_key = ndb.KeyProperty(User, required=True)
    user_id = ndb.StringProperty(required=True)
    link = ndb.KeyProperty(Link, required=True)
    link_id = ndb.StringProperty(required=True)
    tweeted_count = ndb.IntegerProperty(required=True)
    priority = ndb.FloatProperty(required=True)
    scheduled_at = ndb.DateTimeProperty(required=True)
    read_at = ndb.DateTimeProperty()

    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)

    @staticmethod
    def fetchByUser(user):
        userLinks = UserLink.query(UserLink.user_key == user.key).fetch()
        app.logger.info('Fetched {} userLinks for user {}'.format(len(userLinks), user))
        return userLinks
