from twython import Twython

consumer_key = 'G8v4IHt7misK6qliT5eH3p1Rp'
consumer_secret = 'uw3O4u9GXTdS53aS9KEDuSsdbiOLV0kN7MK3H7ZpawbM7yWHh5'
access_token_key = '22895708-O5NdDSJRKxtuTIWrAGxpNaWPKUHG1CTj8QJbjjilS'
access_token_secret = 'sx2KjzCWxPCDOmQhe4cQrYQpT3Y6w0algyBcUaKzMBZXt'

twitter = Twython(
    app_key=consumer_key,
    app_secret=consumer_secret,
    oauth_token=access_token_key,
    oauth_token_secret=access_token_secret
)
print 'twitter: {}'.format(twitter)

results = twitter.cursor(twitter.search, q='#python')
for result in results:
    print result
    break
