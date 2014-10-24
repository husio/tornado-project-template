import tornado.web

from app.handlers import auth


url = tornado.web.URLSpec

urls = (
    url(r'/login', auth.LoginHandler, name='login'),
    url(r'/logout', auth.LogoutHandler, name='logout'),
    url(r'/login/google', auth.GoogleLoginHandler, name='auth-google'),
    url(r'/login/twitter', auth.TwitterLoginHandler, name='auth-twitter'),
)
