import json

import tornado.web
import redis
from sqlalchemy import sql

from app.storage import db


class RequestHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.database_engine

    def get_current_user(self):
        uid = self.get_secure_cookie('uid')
        if not uid:
            return None
        select = sql.select([db.users]).where(db.users.c.id == int(uid))
        result = self.db.execute(select).first()
        if result is None:
            return None
        return dict(result)

    @property
    def current_user_id(self):
        user = self.current_user
        if user:
            return user['id']
        return None

    def redis_connection(self):
        return redis.StrictRedis(connection_pool=self.application.redis_pool)

    def render_string(self, template_name, **kwargs):
        template = self.application.template_env.get_template(template_name)
        context = self.get_template_namespace()
        context.update(kwargs)
        return template.render(context)


class JsonAPIHandler(RequestHandler):
    def finish_json(self, status, content=None):
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_status(status)

        def prepare_json(obj):
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            return obj

        if content:
            self.finish(json.dumps(content, default=prepare_json))
        else:
            self.finish()

    def json_body(self):
        return json.loads(self.request.body.decode('utf8'))
