import functools
from unittest import mock

import sqlalchemy
import tornado.testing

from app.application import create_app
from app.storage import db


DATABASE = 'postgresql://localhost:5432'


class DatabaseTestMixin:
    def setUp(self):
        self.__dbname = 'test_application'
        try:
            _raw_execute('CREATE DATABASE {}'.format(self.__dbname))
        except Exception:
            _raw_execute('DROP DATABASE {}'.format(self.__dbname))
            _raw_execute('CREATE DATABASE {}'.format(self.__dbname))
        self.database_engine = sqlalchemy.create_engine(
            "{}/{}".format(DATABASE, self.__dbname))
        db.metadata.create_all(self.database_engine)
        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.database_engine.dispose()
        _raw_execute('DROP DATABASE {}'.format(self.__dbname))


class HandlerTest(DatabaseTestMixin, tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        from settings import Testing
        options = Testing().as_dict()
        return create_app(database_engine=self.database_engine, **options)


def logged_as(user_id):
    def decorator(method):
        @mock.patch('app.handlers.base.RequestHandler.get_current_user')
        @functools.wraps(method)
        def wrapper(self, get_current_user, *args, **kwargs):
            get_current_user.return_value = {
                'id': user_id,
                'email': 'fake.jack@example.com',
                'name': 'Jack Fake',
            }
            return method(self, *args, **kwargs)

        return wrapper
    return decorator


def _raw_execute(sql):
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

    db = psycopg2.connect(DATABASE)
    db.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    c = db.cursor()
    c.execute(sql)
    c.close()
    db.close()
