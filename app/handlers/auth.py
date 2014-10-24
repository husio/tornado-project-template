import json

import tornado.auth
import tornado.gen
import tornado.httpclient
from sqlalchemy import sql

from app.handlers.base import RequestHandler
from app.storage import db


class LoginHandler(RequestHandler):
    def get(self):
        auth = {
            'google': 'google_oauth' in self.application.settings,
            'twitter': 'twitter_consumer_key' in self.application.settings,
        }
        return self.render("login.html", available_auth=auth)


class LogoutHandler(RequestHandler):
    def get(self):
        self.clear_cookie('uid')
        return self.redirect('/')


class RegisterMixin:
    @tornado.gen.coroutine
    def auth_user(self, provider, uid, email='', name=''):
        ex_id = '{}:{}'.format(provider, uid)
        select = sql.select([db.users]).where(sql.and_(
            db.users.c.id == db.users_auth.c.user_id,
            db.users_auth.c.id == ex_id))

        with self.db.begin() as tx:
            result = tx.execute(select)
            dbuser = result.first()
            if dbuser:
                uid = dbuser.id
            else:
                result = tx.execute(
                    db.users.insert().values(email=email, name=name))
                uid = result.inserted_primary_key[0]
                tx.execute(
                    db.users_auth.insert().values(user_id=uid, id=ex_id))
        self.set_secure_cookie('uid', str(uid))


class GoogleLoginHandler(RequestHandler, tornado.auth.GoogleOAuth2Mixin,
                         RegisterMixin):
    USERINFO_URL = 'https://www.googleapis.com/oauth2/v1/userinfo' \
                   '?access_token={access_token}'

    @tornado.gen.coroutine
    def get(self):
        if not self.application.settings.get('google_oauth'):
            raise tornado.web.HTTPError(404)

        if self.get_argument('code', False):
            credentials = yield self.get_authenticated_user(
                redirect_uri=self.settings['google_auth_redirect_url'],
                code=self.get_argument('code'))
            if not credentials:
                self.clear_all_cookies()
                raise tornado.web.HTTPError(
                    500, 'Google authentication failed')
            url = self.USERINFO_URL.format(**credentials)
            http_client = tornado.httpclient.AsyncHTTPClient()
            response = yield http_client.fetch(url)
            if not response:
                self.clear_all_cookies()
                raise tornado.web.HTTPError(500, 'Google user info failed')
            user = json.loads(response.body.decode('utf8'))
            yield self.auth_user('google', user['id'], user['email'],
                                 user['name'])
            return self.redirect("/")

        yield self.authorize_redirect(
            redirect_uri=self.settings['google_auth_redirect_url'],
            client_id=self.settings['google_oauth']['key'],
            scope=['profile', 'email'], response_type='code',
            extra_params={'approval_prompt': 'auto'})


class TwitterLoginHandler(RequestHandler, tornado.auth.TwitterMixin,
                          RegisterMixin):
    @tornado.gen.coroutine
    def get(self):
        if not self.application.settings.get('twitter_consumer_key'):
            raise tornado.web.HTTPError(404)

        if self.get_argument("oauth_token", None):
            user = yield self.get_authenticated_user()
            yield self.auth_user('twitter', user['id'], name=user['name'])
            return self.redirect("/")
        yield self.authorize_redirect()
