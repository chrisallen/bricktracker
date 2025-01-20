# This need to be first
import eventlet
eventlet.monkey_patch()

import logging  # noqa: E402

from flask import Flask  # noqa: E402

from bricktracker.app import setup_app  # noqa: E402
from bricktracker.socket import BrickSocket  # noqa: E402

logger = logging.getLogger(__name__)

# Create the Flask app
app = Flask(__name__)

# Setup the app
setup_app(app)

# Create the socket
s = BrickSocket(
    app,
    threaded=not app.config['NO_THREADED_SOCKET'],
)


if __name__ == '__main__':
    # Run the application
    logger.info('Starting BrickTracker on {host}:{port}'.format(
        host=app.config['HOST'],
        port=app.config['PORT'],
    ))
    s.socket.run(
        app,
        host=app.config['HOST'],
        debug=app.config['DEBUG'],
        port=app.config['PORT'],
    )
