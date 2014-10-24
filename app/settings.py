import os


PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Configuration:
    project_root = PROJECT_ROOT
    application_root = os.path.join(PROJECT_ROOT, 'app')

    debug = os.getenv('DEBUG', None) in ['yes', '1']
    testing = False

    cookie_secret = 'REPLACE WITH RANDOM STRING'
    login_url = '/login'

    template_path = os.path.join(PROJECT_ROOT, 'templates')

    static_path = os.path.join(PROJECT_ROOT, 'statics')
    static_url_prefix = '/static/'

    log_sql_statements = debug
    database = 'postgresql://@/DATABASE_NAME'

    http_server_port = 5000
    http_server_address = '127.0.0.1'

    google_oauth__key = NotImplemented
    google_oauth__secret = NotImplemented
    google_auth_redirect_url = NotImplemented

    twitter_consumer_key = NotImplemented
    twitter_consumer_secret = NotImplemented

    def as_dict(self):
        conf = {}
        for name in dir(self):
            if name.startswith('_'):
                continue
            value = getattr(self, name)
            if value is NotImplemented:
                continue
            chunks = name.split('__')
            node = conf
            for chunk in chunks[:-1]:
                node = node[chunk] = {}
            node[chunks[-1]] = value
        return conf


class Development(Configuration):
    debug = True
    log_sql_statements = True
    cookie_secret = 'aspidhq[hrqwoh98say98'


class Testing(Configuration):
    debug = False
    testing = True
    cookie_secret = '{{}:DA}{AS(@*^#$'


class Production(Configuration):
    pass
