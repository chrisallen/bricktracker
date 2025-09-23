#!/usr/bin/env python3
"""
WSGI entry point for BrickTracker - Production Docker deployment
This ensures proper gevent monkey patching before any imports
"""

# CRITICAL: Monkey patch must be first, before ANY other imports
import gevent.monkey
gevent.monkey.patch_all()

# Now import the regular app factory
from app import create_app

# Create the application - this will be a BrickSocket instance
app_instance = create_app()

# For gunicorn, we need the Flask app, not the BrickSocket wrapper
application = app_instance.app if hasattr(app_instance, 'app') else app_instance