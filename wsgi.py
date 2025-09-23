#!/usr/bin/env python3
"""
WSGI entry point for BrickTracker - Production Docker deployment
This ensures proper gevent monkey patching for gunicorn
"""

# CRITICAL: This must be the very first import
import gevent.monkey
gevent.monkey.patch_all()

import logging
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import Flask and BrickTracker modules directly
from flask import Flask
from bricktracker.app import setup_app
from bricktracker.socket import BrickSocket

logger = logging.getLogger(__name__)

# Create the Flask app directly (bypassing app.py to avoid double monkey patching)
app = Flask(__name__)

# Setup the app
setup_app(app)

# Create the socket
socket_instance = BrickSocket(
    app,
    threaded=not app.config['NO_THREADED_SOCKET'],
)

# Export the Flask app for gunicorn
application = app