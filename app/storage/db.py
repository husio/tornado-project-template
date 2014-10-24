import datetime

import pytz
import sqlalchemy as sa


metadata = sa.MetaData()


def now():
    return datetime.datetime.now(tz=pytz.utc)


users = sa.Table(
    "users", metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("email", sa.String, default='', nullable=False),
    sa.Column("name", sa.String, default='', nullable=False),
)


users_auth = sa.Table(
    "users_auth", metadata,
    sa.Column("id", sa.String, primary_key=True),
    sa.Column("user_id", None, sa.ForeignKey('users.id'), nullable=False),
    sa.Column("created", sa.DateTime, default=now, nullable=False),
)
