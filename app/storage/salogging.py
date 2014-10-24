import weakref
import time

import sqlalchemy
import sqlparse
import pygments
from pygments.lexers.sql import PostgresLexer
from pygments.formatters import Terminal256Formatter


_cursors = weakref.WeakKeyDictionary()


def before_execute(conn, cursor, statement, parameters, context, executemany):
    sql = str(statement)
    code = sqlparse.format(sql, reindent=True, keyword_case='upper',
                           truncate_strings=12)
    out = pygments.highlight(code, PostgresLexer(),
                             Terminal256Formatter(style='monokai'))
    _cursors[cursor] = time.time()
    print(out)


def after_execute(conn, cursor, statement, parameters, context, executemany):
    start_time = _cursors.pop(cursor, None)
    if not start_time:
        return
    work_time = (time.time() - start_time) * 1000
    print("query time: {:.2}ms\n".format(work_time))


def log_sql(engine):
    sqlalchemy.event.listen(engine, "before_cursor_execute", before_execute)
    sqlalchemy.event.listen(engine, "after_cursor_execute", after_execute)
