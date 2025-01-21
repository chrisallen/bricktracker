# This need to be first
import eventlet
eventlet.monkey_patch()

import logging  # noqa: E402

from flask import Flask  # noqa: E402

from bricktracker.app import setup_app  # noqa: E402
from bricktracker.socket import BrickSocket  # noqa: E402

logger = logging.getLogger(__name__)


# Create the app
# Using 'app' globally interferse with the teardown handlers of Flask
def create_app(main: bool = False, /) -> Flask | BrickSocket:
    # Create the Flask app
    app = Flask(__name__)

    # Setup the app
    setup_app(app)

    # Create the socket
    s = BrickSocket(
        app,
        threaded=not app.config['NO_THREADED_SOCKET'],
    )

    if main:
        return s
    else:
        return app


if __name__ == '__main__':
    s = create_app(True)

    # This never happens, but makes the linter happy
    if isinstance(s, Flask):
        logger.critical('Cannot run locally with a Flask object, needs a BrickSocket. Use create_app(True) to return a BrickSocket')  # noqa: E501
        exit(1)

    # Run the application
    logger.info('Starting BrickTracker on {host}:{port}'.format(
        host=s.app.config['HOST'],
        port=s.app.config['PORT'],
    ))
    s.socket.run(
        s.app,
        host=s.app.config['HOST'],
        debug=s.app.config['DEBUG'],
        port=s.app.config['PORT'],
    )
