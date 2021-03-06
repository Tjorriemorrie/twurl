from src import app
from flask import request, render_template, json, Response, abort, redirect
from models import User, Tweet, Link, UserLink
import urllib
import base64
from google.appengine.api import urlfetch, taskqueue, mail
import datetime
import math
from flask.ext.jsontools import jsonapi
import urlparse
import oauth2 as oauth


@app.route('/')
def index():
    token = obtainRequestToken()
    params = {
    }
    app.logger.info('index: {}'.format(params))
    return render_template('index.html', **params)


def obtainRequestToken():
    app.logger.info('Obtaining request token')

    app.logger.info('Creating oauth consumer...')
    consumer = oauth.Consumer(app.config['CONSUMER_KEY'], app.config['CONSUMER_SECRET'])

    app.logger.info('Creating oauth client...')
    client = oauth.Client(consumer)

    app.logger.info('Requesting token from twitter...')
    resp, content = client.request(app.config['REQUEST_TOKEN_URL'], 'GET')
    if resp['status'] != '200':
        raise Exception("Invalid response %s." % resp['status'])

    request_token = dict(urlparse.parse_qsl(content))
    app.logger.info('Request token received: {}'.format(request_token))
    return request_token


@app.route('/twitter_callback')
def twitterCallback():
    form_data = request.form
    app.logger.info('form_data: {}'.format(form_data))
    return redirect('/')


###########################################
# USER
###########################################

@app.route('/user', methods=['GET', 'POST'])
@jsonapi
def user():
    app.logger.info('formdata {}'.format(request.form))
    email = request.form.get('email')
    password = request.form.get('password')
    # todo validation
    user = User.authenticate(email, password)
    # todo return proper token
    return user.key.urlsafe()


@app.route('/user/main', methods=['GET', 'POST'])
@jsonapi
def userMain():

    # todo ensure twurlie is topic if none
    data = {}

    # get user
    app.logger.info('formdata {}'.format(request.form))
    user_key = request.form.get('user_key')
    user = User.fetchByKey(user_key)
    if not user:
        abort(403)

    # get last userlink per topic
    for topic in user.topics:
        userLink = UserLink.findLastByUser(topic, user)
        if userLink:
            data[topic] = {
                'key': userLink.key.urlsafe(),
                'link_id': userLink.link_id,
                'tweeted_count': userLink.tweeted_count,
                'priority': userLink.priority,
                'read_at': hasattr(userLink, 'read_at') and userLink.read_at
            }
        else:
            data[topic] = None

    return data


@app.route('/user/read', methods=['GET', 'POST'])
@jsonapi
def userRead():

    # get user
    app.logger.info('formdata {}'.format(request.form))
    user_key = request.form.get('user_key')
    user = User.fetchByKey(user_key)
    if not user:
        abort(403)

    # mark last link
    topic = request.form.get('topic')
    userLink = UserLink.readLastByUser(topic, user)

    return userLink.read_at


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


###########################################
# LINKS SCHEDULING
###########################################
# NB this is run first before quota is filled
# 1st create task queue for every topic
# 2nd link every user's every topic

@app.route('/cron/schedule/links', methods=['GET', 'POST'])
def scheduleLinks():
    ''' Run this after quota reset '''
    # get topics
    user_topics = User.query(projection=[User.topics], distinct=True).fetch()
    topics = [user.topics[0] for user in user_topics]
    app.logger.info('Topics fetched: {}'.format(topics))

    for topic in topics:
        taskqueue.add(url='/cron/schedule/link', params={'topic': topic})
        app.logger.info('Created push queue to schedule link for {}'.format(topic))

    mail.send_mail(
        sender='jacoj82@gmail.com',
        to='jacoj82@gmail.com',
        subject='Schedule Links',
        body='All {} topics pushed'.format(len(topics)),
    )

    app.logger.info('All {} topics pushed'.format(len(topics)))
    return Response('OK')


@app.route('/cron/schedule/link', methods=['GET', 'POST'])
def scheduleLink():
    if request.method == 'POST':
        app.logger.info('request form: {}'.format(request.form))
        topic = request.form.get('topic')
    elif request.method == 'GET':
        app.logger.info('request args: {}'.format(request.args))
        topic = request.args.get('topic')
    if not topic:
        abort(400)
    app.logger.info('Topic param received: {}'.format(topic))

    # get users by topic
    users = User.fetchByTopic(topic)

    # get ordered links by topic
    # two inequality filters not supported
    week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    links = Link.fetchByTopic(topic)

    spamLinks = []
    info = {}
    # for every user
    for user in users:
        info[user.email] = None

        # get last userlink:
        # if not read => skip
        # if too soon => skip
        lastUserLink = UserLink.findLastByUser(topic, user)
        if lastUserLink and not hasattr(lastUserLink, 'read'):
            app.logger.info('User has unread UserLink')
            continue

        # then loop through ordered links
        for link in links:
            # skip links that has been spammed
            # ignore links created before a week ago
            # these links will go away since updated_at will keep renewing
            if link.created_at < week_ago:
                app.logger.debug('Skipping spam link: {}'.format(link.id))
                spamLinks.append(link.id)
                continue

            # and assign first non-userlink to user
            # note: search without topic:
            # this gives unique link for a list of similar topics
            if not UserLink.findByUserAndLink(user, link):
                # assign new userlink to user for the topic
                UserLink.create(topic, user, link)
                info[user.email] = link.id
                break

    body = '\n'.join(['User {} got link {}'.format(userEmail, linkId) for userEmail, linkId in info.iteritems()])
    body += '\n'.join(spamLinks)
    mail.send_mail(
        sender='jacoj82@gmail.com',
        to='jacoj82@gmail.com',
        subject='Schedule Link {}'.format(topic),
        body=body,
    )

    app.logger.info('{} users got links'.format(len(info)))
    return Response('OK')


###########################################
# SCRAPING TWITTER
###########################################
# NB this is run last as the quota will never be sufficient
# remember to set timeout on task queue so it does not carry over reset
# 1st is to create task queues for every topic
# 2nd remove expired tweets (hold about 1 month - depends on datastore size)
# 3rd delete expired urls/links (hold about 1 month (created between 7 days and 1 months is spam)
# 4th score the urls based on tweets and retweets

# 2nd link every user's every topic

@app.route('/cron/topics', methods=['GET', 'POST'])
def cronTopics():

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
        taskqueue.add(url='/cron/remove/tweets', params=params)

    mail.send_mail(
        sender='jacoj82@gmail.com',
        to='jacoj82@gmail.com',
        subject='Cron Topics',
        body='All {} topics pushed'.format(len(topics)),
    )

    app.logger.info('All {} topics pushed'.format(len(topics)))
    return Response('OK')


@app.route('/cron/remove/tweets', methods=['GET', 'POST'])
def removeTweets():
    if request.method == 'POST':
        app.logger.info('request form: {}'.format(request.form))
        topic = request.form.get('topic')
    elif request.method == 'GET':
        app.logger.info('request args: {}'.format(request.args))
        topic = request.args.get('topic')
    if not topic:
        abort(400)
    app.logger.info('Topic param received: {}'.format(topic))

    # delete old tweets (> 1 year)
    cnt = Tweet.removeOld(datetime.datetime.utcnow() - datetime.timedelta(days=30), topic)

    # continue with deleting urls
    taskqueue.add(url='/cron/delete/urls', params={'topic': topic})

    # mail.send_mail(
    #     sender='jacoj82@gmail.com',
    #     to='jacoj82@gmail.com',
    #     subject='Remove tweets {}'.format(topic),
    #     body='{} tweets deleted for topic {}'.format(cnt, topic),
    # )

    app.logger.info('{} tweets deleted for topic {}'.format(cnt, topic))
    return Response('OK')


@app.route('/cron/delete/urls', methods=['GET', 'POST'])
def deleteUrls():
    if request.method == 'POST':
        app.logger.info('request form: {}'.format(request.form))
        topic = request.form.get('topic')
    elif request.method == 'GET':
        app.logger.info('request args: {}'.format(request.args))
        topic = request.args.get('topic')
    if not topic:
        abort(400)
    app.logger.info('Topic param received: {}'.format(topic))

    cnt = Link.removeOld(topic, datetime.datetime.utcnow() - datetime.timedelta(days=30))

    # continue with scoring urls
    taskqueue.add(url='/cron/score/urls', params={'topic': topic})

    # mail.send_mail(
    #     sender='jacoj82@gmail.com',
    #     to='jacoj82@gmail.com',
    #     subject='Delete Urls {}'.format(topic),
    #     body='Removed {} links for topic {}'.format(cnt, topic),
    # )


    return Response('OK')


@app.route('/cron/score/urls', methods=['GET', 'POST'])
def scoreUrls():
    if request.method == 'POST':
        app.logger.info('request form: {}'.format(request.form))
        topic = request.form.get('topic')
    elif request.method == 'GET':
        app.logger.info('request args: {}'.format(request.args))
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
                app.logger.debug('Url added: {}'.format(url))
            urlScores[url]['tweeted_count'] += 1
            urlScores[url]['retweeted_sum'] += math.log(max(1, tweet.retweet_count))
            urlScores[url]['favorite_sum'] += math.log(max(1, tweet.favorite_count))
    app.logger.info('All {} tweets parsed and found {} urls'.format(len(tweets), len(urlScores)))

    app.logger.info('Saving urls...')
    for url, url_info in urlScores.iteritems():
        link = Link.create(topic, url, url_info)

    # continue to scrape for new tweets
    taskqueue.add(url='/cron/topic', params={'topic': topic})
    app.logger.info('Task created to scrape for new tweets for {}'.format(topic))

    mail.send_mail(
        sender='jacoj82@gmail.com',
        to='jacoj82@gmail.com',
        subject='Score urls {}'.format(topic),
        body='{} tweets created {} urls'.format(len(tweets), len(urlScores)),
    )

    app.logger.info('Scoring urls done for {}'.format(topic))
    return Response('OK')


@app.route('/cron/topic', methods=['GET', 'POST'])
def cronTopic():

    access_token = 'AAAAAAAAAAAAAAAAAAAAABcJYAAAAAAAVviSzyKtPYqYlHpZxoim6DHvfjI%3DU0slNkvBKQRynT62gbvQjEhAlE2PvzVZNia99xAdoJweI2OLqe'

    if request.method == 'POST':
        app.logger.info('request form: {}'.format(request.form))
        topic = request.form.get('topic')
    elif request.method == 'GET':
        app.logger.info('request args: {}'.format(request.args))
        topic = request.args.get('topic')
    if not topic:
        abort(400)

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
        'result_type': 'recent',
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

    cnt = 0
    max_cnt = 90 if app.config['DEBUG'] else 1222333
    while cnt < max_cnt:
        content = json.loads(res.content)
        metadata = content['search_metadata']
        statuses = content['statuses']
        # app.logger.info('Metadata: {}'.format(metadata))
        # app.logger.info('Statuses: {}'.format(len(statuses)))
        cnt += len(statuses)

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

    # continue with nothing, quota will be obliterated with this

    mail.send_mail(
        sender='jacoj82@gmail.com',
        to='jacoj82@gmail.com',
        subject='Cron topic {}'.format(topic),
        body='Scraped {} tweets for topic {}'.format(cnt, topic),
    )

    app.logger.info('Scraped {} tweets for topic {}'.format(cnt, topic))
    return Response('OK')


