from src import app
from google.appengine.ext import ndb


class Product(ndb.Model):
    name = ndb.StringProperty(required=True)
    is_active = ndb.BooleanProperty(required=True)
    available_at = ndb.DateTimeProperty(required=True)
    ended_at = ndb.DateTimeProperty(required=True)
    cost = ndb.FloatProperty(required=True)

    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)

    @staticmethod
    def getCurrentUser():
        user_session = users.get_current_user()
        app.logger.info('User get current user: {}'.format(user_session))

        # no user
        if not user_session:
            return User()

        # search user
        user = User.query().filter(User.email == user_session.email()).get()

        # create if not exist
            user = User(nickname=user_session.nickname(), email=user_session.email())
        if not user:
            user.put()
            app.logger.info('New user created: {}'.format(user))

        return user

    @property
    def signInUrl(self):
        url = users.create_login_url('/client')
        app.logger.info('User Signin: {}'.format(url))
        return url

    @property
    def signOutUrl(self):
        url = users.create_logout_url('/')
        app.logger.info('User Signout: {}'.format(url))
        return url

    @property
    def isAdmin(self):
        isAdmin = users.is_current_user_admin()
        app.logger.info('User isAdmin: {}'.format(isAdmin))
        return isAdmin
