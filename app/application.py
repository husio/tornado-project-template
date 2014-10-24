import jinja2
import tornado.web
import sqlalchemy
import redis

from app.storage import db, salogging
from app.urls import urls


class Application(tornado.web.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.settings = kwargs

        # setup templates
        template_loader = jinja2.FileSystemLoader(
            searchpath=kwargs['template_path'])
        self.template_env = jinja2.Environment(loader=template_loader)

        # setup sql database connection
        engine = sqlalchemy.create_engine(kwargs['database'])
        if kwargs.get('log_sql_statements'):
            salogging.log_sql(engine)
        db.metadata.create_all(engine)
        self.database_engine = engine

        # setup redis connection
        self.redis_pool = redis.ConnectionPool(db=1)


def create_application(**options):
    return Application(urls, **options)
