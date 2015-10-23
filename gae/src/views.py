from src import app
from flask import request, render_template, json, Response, abort
from models import User, Tweet, Link, UserLink
import urllib
import base64
from google.appengine.api import urlfetch, taskqueue, mail
import datetime
import math
from flask.ext.jsontools import jsonapi


@app.route('/')
def index():
    params = {
    }
    app.logger.info('index: {}'.format(params))
    return render_template('base.html', **params)


###########################################
# USER
###########################################

@app.route('/user', methods=['GET', 'POST'])
@jsonapi
def user():
    app.logger.info('args {}'.format(request.args))
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
    data = []

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
            data.append({
                'topic': topic,
                'key': userLink.key.urlsafe(),
                'link_id': userLink.link_id,
                'tweeted_count': userLink.tweeted_count,
                'priority': userLink.priority,
                'read_at': hasattr(userLink, 'read_at') and userLink.read_at
            })
        else:
            data.append({
                'topic': topic,
            })

    app.logger.info('Data: {}'.format(data))
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

@app.route('/cron/schedule/links')
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


@app.route('/cron/schedule/link', methods=['POST'])
def scheduleLink():
    app.logger.info('request form: {}'.format(request.form))
    topic = request.form.get('topic')
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
            info[user.email] = 'User has unread UserLink'
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

    body = '\n'.join(['{}: {}'.format(userEmail, linkId) for userEmail, linkId in info.iteritems()])
    body += '\n'.join(spamLinks)
    mail.send_mail(
        sender='jacoj82@gmail.com',
        to='jacoj82@gmail.com',
        subject='Schedule Link {}'.format(topic),
        body=body,
    )
    app.logger.info(body)

    app.logger.info('{} users got links'.format(len(info)))
    return Response('OK')


###########################################
# SCRAPING TWITTER
###########################################
# NB this is run last as the quota will never be sufficient
# remember to set timeout on task queue so it does not carry over reset
# 1st is to create task queues for every topic
# 2nd remove expired tweets (hold about 12 months - depends on datastore size)
# 3rd delete expired urls/links (hold about 1 month (created between 7 days and 1 months is spam)
# 4th score the urls based on tweets and retweets


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
        params = {'topic': topic}
        app.logger.info('Scheduled remove tweets for {}'.format(params))
        taskqueue.add(url='/cron/remove/tweets', params=params)

    mail.send_mail(
        sender='jacoj82@gmail.com',
        to='jacoj82@gmail.com',
        subject='Cron Topics',
        body='All {} topics pushed: {}'.format(len(topics), topics),
    )

    app.logger.info('All {} topics pushed'.format(len(topics)))
    return Response('OK')


@app.route('/cron/remove/tweets', methods=['POST'])
def removeTweets():
    app.logger.info('request form: {}'.format(request.form))
    topic = request.form.get('topic')
    if not topic:
        abort(400)
    app.logger.info('Topic param received: {}'.format(topic))

    # delete old tweets (> 1 year)
    cnt = Tweet.removeOld(datetime.datetime.utcnow() - datetime.timedelta(days=360), topic)

    # continue with deleting urls
    params = {'topic': topic}
    app.logger.info('Scheduled delete urls for {}'.format(params))
    taskqueue.add(url='/cron/delete/urls', params=params)

    # mail.send_mail(
    #     sender='jacoj82@gmail.com',
    #     to='jacoj82@gmail.com',
    #     subject='Remove tweets {}'.format(topic),
    #     body='{} tweets deleted for topic {}'.format(cnt, topic),
    # )

    app.logger.info('{} tweets deleted for topic {}'.format(cnt, topic))
    return Response('OK')


@app.route('/cron/delete/urls', methods=['POST'])
def deleteUrls():
    app.logger.info('request form: {}'.format(request.form))
    topic = request.form.get('topic')
    if not topic:
        abort(400)
    app.logger.info('Topic param received: {}'.format(topic))

    cnt = Link.removeOld(topic, datetime.datetime.utcnow() - datetime.timedelta(days=30))

    # continue with scoring urls
    params = {'topic': topic}
    app.logger.info('Scheduled scraping topic for {}'.format(params))
    taskqueue.add(url='/cron/topic', params={'topic': topic})

    # mail.send_mail(
    #     sender='jacoj82@gmail.com',
    #     to='jacoj82@gmail.com',
    #     subject='Delete Urls {}'.format(topic),
    #     body='Removed {} links for topic {}'.format(cnt, topic),
    # )

    app.logger.info('{} urls deleted for topic {}'.format(cnt, topic))
    return Response('OK')


@app.route('/cron/topic', methods=['POST'])
def cronTopic():
    # Requests / 15-min window (user auth)  180
    # Requests / 15-min window (app auth)   450
    # 450 / (15 * 60) = 0.5 per second
    # thus 1 request every 2 seconds
    access_token = 'AAAAAAAAAAAAAAAAAAAAABcJYAAAAAAAVviSzyKtPYqYlHpZxoim6DHvfjI%3DU0slNkvBKQRynT62gbvQjEhAlE2PvzVZNia99xAdoJweI2OLqe'
    body = ''

    app.logger.info('request form: {}'.format(request.form))
    topic = request.form.get('topic')
    if not topic:
        abort(400)
    body += 'Topic {}\n\n'.format(topic)

    # this can be original (get since_id) or repeated (use next_results)
    next_results = request.form.get('next_results', None)
    if next_results:
        app.logger.info('Scraping next page results')
        res = urlfetch.fetch(
            url='{}{}'.format('https://api.twitter.com/1.1/search/tweets.json', next_results),
            method=urlfetch.GET,
            headers={
                'Authorization': 'Bearer {}'.format(access_token),
            },
        )
    else:
        app.logger.info('Scraping with since id')
        # get since ID
        since_id = Tweet.since_id(topic)
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
            'count': 10,
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

    # parse response
    app.logger.info('Processing response from twitter')
    content = json.loads(res.content)
    metadata = content['search_metadata']
    statuses = content['statuses']
    # app.logger.info('Metadata: {}'.format(metadata))
    app.logger.info('Statuses: {}'.format(len(statuses)))
    body += '{} statuses found\n\n'.format(len(statuses))

    # process tweets
    for status in statuses:
        tweet = Tweet.create(topic, status)
        # score url
        for url in tweet.urls:
            # expand url
            #http://api.longurl.org/v2/expand?url=http%3A%2F%2Fis.gd%2Fw
            # upsert url
            link = Link.upsert(topic, url, tweet.retweet_count)
            body += '{}: {}\n'.format(link.tweet_count, link.id)

    # continue scraping
    if 'next_results' not in metadata:
        app.logger.info('No more statuses')
    elif not app.config['DEBUG']:
        params = {'topic': topic, 'next_results': metadata['next_results']}
        app.logger.info('Scheduled scraping topic for {}'.format(params))
        taskqueue.add(url='/cron/topic', params={'topic': topic})

    mail.send_mail(
        sender='jacoj82@gmail.com',
        to='jacoj82@gmail.com',
        subject='Cron topic {}'.format(topic),
        body=body,
    )

    app.logger.info('Scraped {} tweets for topic {}'.format(len(statuses), topic))
    return Response('OK')
