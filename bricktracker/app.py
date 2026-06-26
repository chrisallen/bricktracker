import logging
import os
import sys
import time
from pathlib import Path
from zoneinfo import ZoneInfo

from flask import current_app, Flask, g
from werkzeug.middleware.proxy_fix import ProxyFix

from bricktracker.configuration_list import BrickConfigurationList
from bricktracker.login import LoginManager
from bricktracker.navbar import Navbar
from bricktracker.sidecar import BrickSidecar
from bricktracker.sql import close
from bricktracker.template_filters import replace_query_filter
from bricktracker.version import __version__
from bricktracker.views.add import add_page
from bricktracker.views.admin.admin import admin_page
from bricktracker.views.admin.custom_field import admin_custom_field_page
from bricktracker.views.admin.database import admin_database_page
from bricktracker.views.admin.export import admin_export_page
from bricktracker.views.admin.image import admin_image_page
from bricktracker.views.admin.instructions import admin_instructions_page
from bricktracker.views.admin.owner import admin_owner_page
from bricktracker.views.admin.purchase_location import admin_purchase_location_page  # noqa: E501
from bricktracker.views.admin.retired import admin_retired_page
from bricktracker.views.admin.set import admin_set_page
from bricktracker.views.admin.status import admin_status_page
from bricktracker.views.admin.storage import admin_storage_page
from bricktracker.views.admin.tag import admin_tag_page
from bricktracker.views.admin.theme import admin_theme_page
from bricktracker.views.data import data_page
from bricktracker.views.error import error_404
from bricktracker.views.index import index_page
from bricktracker.views.individual_minifigure import individual_minifigure_page
from bricktracker.views.individual_part import individual_part_page
from bricktracker.views.instructions import instructions_page
from bricktracker.views.login import login_page
from bricktracker.views.minifigure import minifigure_page
from bricktracker.views.part import part_page
from bricktracker.views.purchase_location import purchase_location_page
from bricktracker.views.set import set_page
from bricktracker.views.statistics import statistics_page
from bricktracker.views.storage import storage_page
from bricktracker.views.wish import wish_page


def load_env_file() -> None:
    """Load .env file into os.environ with priority: data/.env > .env (root)

    Also stores which BK_ variables were set via Docker environment (before loading .env)
    so we can detect locked variables in the admin panel.
    """
    import json

    data_env = Path('data/.env')
    root_env = Path('.env')

    # Store which BK_ variables were already in environment BEFORE loading .env
    # These are "locked" (set via Docker's environment: directive)
    docker_env_vars = {k: v for k, v in os.environ.items() if k.startswith('BK_')}

    # Store this in a way the admin panel can access it
    # We'll use an environment variable to store the JSON list of locked var names
    os.environ['_BK_DOCKER_ENV_VARS'] = json.dumps(list(docker_env_vars.keys()))

    env_file = None
    if data_env.exists():
        env_file = data_env
        logging.info(f"Loading environment from: {data_env}")
    elif root_env.exists():
        env_file = root_env
        logging.info(f"Loading environment from: {root_env} (consider migrating to data/.env)")

    if env_file:
        # Simple .env parser (no external dependencies needed)
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                # Parse key=value
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    # Only set if not already in environment (environment variables take precedence)
                    if key not in os.environ:
                        os.environ[key] = value


def setup_app(app: Flask) -> None:
    # Load .env file before configuration (if not already loaded by Docker Compose)
    load_env_file()

    # Load the configuration
    BrickConfigurationList(app)

    # Set the logging level
    if app.config['DEBUG']:
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.DEBUG,
            format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',  # noqa: E501
        )
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.INFO,
            format='[%(asctime)s] %(levelname)s - %(message)s',
        )
        logging.getLogger().setLevel(logging.INFO)

    # Load the navbar
    Navbar(app)

    # Setup the login manager
    LoginManager(app)

    # Configure proxy header handling for reverse proxy deployments (nginx, Apache, etc.)
    # This ensures proper client IP detection and HTTPS scheme recognition
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
        x_port=1,
        x_prefix=1,
    )

    # Register errors
    app.register_error_handler(404, error_404)

    # Register app routes
    app.register_blueprint(add_page)
    app.register_blueprint(data_page)
    app.register_blueprint(index_page)
    app.register_blueprint(individual_minifigure_page)
    app.register_blueprint(individual_part_page)
    app.register_blueprint(instructions_page)
    app.register_blueprint(login_page)
    app.register_blueprint(minifigure_page)
    app.register_blueprint(part_page)
    app.register_blueprint(purchase_location_page)
    app.register_blueprint(set_page)
    app.register_blueprint(statistics_page)
    app.register_blueprint(storage_page)
    app.register_blueprint(wish_page)

    # Register admin routes
    app.register_blueprint(admin_page)
    app.register_blueprint(admin_custom_field_page)
    app.register_blueprint(admin_database_page)
    app.register_blueprint(admin_export_page)
    app.register_blueprint(admin_image_page)
    app.register_blueprint(admin_instructions_page)
    app.register_blueprint(admin_retired_page)
    app.register_blueprint(admin_owner_page)
    app.register_blueprint(admin_purchase_location_page)
    app.register_blueprint(admin_set_page)
    app.register_blueprint(admin_status_page)
    app.register_blueprint(admin_storage_page)
    app.register_blueprint(admin_tag_page)
    app.register_blueprint(admin_theme_page)

    # An helper to make global variables available to the
    # request
    @app.before_request
    def before_request() -> None:
        def request_time() -> str:
            elapsed = time.time() - g.request_start_time
            if elapsed < 1:
                return '{elapsed:.0f}ms'.format(elapsed=elapsed*1000)
            else:
                return '{elapsed:.2f}s'.format(elapsed=elapsed)

        # Login manager
        g.login = LoginManager

        # Execution time
        g.request_start_time = time.time()
        g.request_time = request_time

        # Register the timezone
        g.timezone = ZoneInfo(current_app.config['TIMEZONE'])

        # Version
        g.version = __version__

    # Register custom Jinja2 filters
    app.jinja_env.filters['replace_query'] = replace_query_filter

    # Expose the sidecar feature flag and helper to every template so they can
    # do `{% if sidecar_enabled %}`. Health is best-effort and cached, so this
    # is cheap to evaluate on render and never blocks on a dead sidecar.
    @app.context_processor
    def inject_sidecar() -> dict[str, object]:
        return {
            'sidecar_enabled': BrickSidecar.enabled(),
            'sidecar': BrickSidecar,
        }

    # Make sure all connections are closed at the end
    @app.teardown_request
    def teardown_request(_: BaseException | None) -> None:
        close()
