from src import app
from flask import request, render_template, json, Response, abort
from models import User, Tweet, Link
import urllib
import base64
from google.appengine.api import urlfetch, taskqueue
import datetime
import math


@app.route('/')
def index():
    params = {
    }
    app.logger.info('index: {}'.format(params))
    return render_template('base.html', **params)


@app.route('/create/user')
def userCreate():
    user = User(email='jacoj82@gmail.com')
    user.put()
    params = {
        'user': user,
    }
    app.logger.info('userCreate: {}'.format(params))
    return render_template('base.html', **params)


@app.route('/topic/create')
def topicCreate():
    user = User.query(User.email == 'jacoj82@gmail.com').get()
    topics = ['python', 'html5']
    user.topics = topics
    params = {
        'user': user,
        'topics': topics,
    }
    user.put()
    app.logger.info('topicCreate: {}'.format(params))
    return render_template('base.html', **params)


@app.route('/cron/topics')
def cronTopics():

    consumer_key = 'G8v4IHt7misK6qliT5eH3p1Rp'
    consumer_secret = 'uw3O4u9GXTdS53aS9KEDuSsdbiOLV0kN7MK3H7ZpawbM7yWHh5'
    access_token_key = '22895708-O5NdDSJRKxtuTIWrAGxpNaWPKUHG1CTj8QJbjjilS'
    access_token_secret = 'sx2KjzCWxPCDOmQhe4cQrYQpT3Y6w0algyBcUaKzMBZXt'

    # res = urlfetch.fetch(
    #     url='https://api.twitter.com/oauth2/token',
    #     payload='grant_type=client_credentials',
    #     method=urlfetch.POST,
    #     headers={
    #         'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    #         'Authorization': 'Basic {}'.format(bearer_token_encoded),
    #     },
    # )
    # app.logger.info(res)
    #
    # data = json.loads(res.content)
    # app.logger.info('Data: {}'.format(data))
    # if 'errors' in data:
    #     error = data['errors'][0]
    #     raise Exception('[{} {}] {}'.format(error['code'], error['label'], error['message']))
    # access_token = data['access_token']
    # token_type = data['token_type']

    # bearer_token = '{}:{}'.format(consumer_key, consumer_secret)
    # app.logger.info('bearer token: {}'.format(bearer_token))
    # bearer_token_encoded = base64.b64encode(bearer_token)
    # app.logger.info('bearer token encoded: {}'.format(bearer_token_encoded))

    access_token = 'AAAAAAAAAAAAAAAAAAAAABcJYAAAAAAAVviSzyKtPYqYlHpZxoim6DHvfjI%3DU0slNkvBKQRynT62gbvQjEhAlE2PvzVZNia99xAdoJweI2OLqe'

    # get topics
    user_topics = User.query(projection=[User.topics], distinct=True).fetch()
    topics = [user.topics[0] for user in user_topics]
    app.logger.info('Topics fetched: {}'.format(topics))

    for topic in topics:
        # get since ID
        since_id = Tweet.since_id(topic)
        params = {'topic': topic, 'since_id': since_id}
        app.logger.info('Created push queue for {}'.format(params))
        taskqueue.add(url='/cron/topic', params=params)

    app.logger.info('All topics pushed')
    return Response('OK')


@app.route('/cron/topic', methods=['GET', 'POST'])
def cronTopic():

    access_token = 'AAAAAAAAAAAAAAAAAAAAABcJYAAAAAAAVviSzyKtPYqYlHpZxoim6DHvfjI%3DU0slNkvBKQRynT62gbvQjEhAlE2PvzVZNia99xAdoJweI2OLqe'

    topic = request.form.get('topic')
    since_id = request.form.get('since_id')
    app.logger.info('Topic params received: {} {}'.format(topic, since_id))

    # Requests / 15-min window (user auth)  180
    # Requests / 15-min window (app auth)   450
    # 450 / (15 * 60) = 0.5 per second
    # thus 1 request every 2 seconds
    month_ago = datetime.datetime.utcnow() - datetime.timedelta(days=30)
    day_ago = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    params = urllib.urlencode({
        'q': 'filter:links since:{} until:{} #{} -filter:retweets'.format(
            month_ago.strftime('%Y-%m-%d'),
            day_ago.strftime('%Y-%m-%d'),
            topic,
        ),
        'result_type': 'popular',
        'include_entities': 1,
        'count': 100,
        'since_id': since_id,
    })
    # count, until, since_id, max_id
    app.logger.info('params {}'.format(params))
    res = urlfetch.fetch(
        url='https://api.twitter.com/1.1/search/tweets.json?{}'.format(params),
        method=urlfetch.GET,
        headers={
            'Authorization': 'Bearer {}'.format(access_token),
        },
    )
    app.logger.info(res)

    while True:
        content = json.loads(res.content)
        metadata = content['search_metadata']
        statuses = content['statuses']
        # app.logger.info('Metadata: {}'.format(metadata))
        # app.logger.info('Statuses: {}'.format(len(statuses)))

        for status in statuses:
            app.logger.info('Processing status')
            tweet = Tweet.create(topic, status)

        if 'next_results' not in metadata:
            app.logger.info('No more statuses')
            break
        else:
            app.logger.info('Fetching more results at {}'.format(metadata['next_results']))
            res = urlfetch.fetch(
                url='{}{}'.format('https://api.twitter.com/1.1/search/tweets.json', metadata['next_results']),
                method=urlfetch.GET,
                headers={
                    'Authorization': 'Bearer {}'.format(access_token),
                },
            )

    app.logger.info('Scraping topic {} finished'.format(topic))

    taskqueue.add(url='/cron/remove/tweets', params={'topic': topic})
    app.logger.info('Task created to remove tweets for {}'.format(topic))

    return Response('OK')


@app.route('/cron/remove/tweets', methods=['GET', 'POST'])
def removeTweets():
    topic = request.args.get('topic')
    if not topic:
        abort(400)
    app.logger.info('Topic param received: {}'.format(topic))

    # delete old tweets (> 1 year)
    Tweet.removeOld(datetime.datetime.utcnow() - datetime.timedelta(days=30), topic)

    # taskqueue.add(url='/cron/remove/tweets', params={'topic': topic})
    # app.logger.info('Task created to remove tweets for {}'.format(topic))

    return Response('OK')


@app.route('/cron/score/urls', methods=['GET', 'POST'])
def scoreUrls():
    topic = request.args.get('topic')
    if not topic:
        abort(400)
    app.logger.info('Topic param received: {}'.format(topic))

    tweets = Tweet.fetchByTopic(topic)

    # group by url and add score
    urlScores = {}
    for tweet in tweets:
        for url in tweet.urls:
            if url not in urlScores:
                urlScores[url] = {
                    'id': url,
                    'tweeted_count': 0,
                    'retweeted_sum': 0.,
                    'favorite_sum': 0.,
                }
            app.logger.debug(tweet)
            urlScores[url]['tweeted_count'] += 1
            urlScores[url]['retweeted_sum'] += math.log(max(1, tweet.retweet_count))
            urlScores[url]['favorite_sum'] += math.log(max(1, tweet.favorite_count))
            app.logger.debug('Tweet values: {} for {}'.format(urlScores[url], url))
        break

    for url, url_info in urlScores.iteritems():
        link = Link.create(topic, url, url_info)

    return Response('OK')


    # delete old urls

