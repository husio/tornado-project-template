import os
import sys

import tornado.ioloop

from app import settings
from app.application import create_application


SETTINGS = os.getenv('SETTINGS', 'Development')


def main():
    try:
        configuration = getattr(settings, SETTINGS)()
    except AttributeError:
        sys.exit("Settings not found: {}".format(SETTINGS))
    sys.stdout.write("Using {} settings\n".format(SETTINGS))

    app = create_application(**configuration.as_dict())
    app.listen(port=configuration.http_server_port,
               address=configuration.http_server_address)
    loop = tornado.ioloop.IOLoop.instance()
    loop.start()


if __name__ == "__main__":
    main()
