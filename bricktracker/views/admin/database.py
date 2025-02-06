from datetime import datetime
import logging
import os

from flask import (
    Blueprint,
    current_app,
    g,
    redirect,
    request,
    render_template,
    send_file,
    url_for,
)
from flask_login import login_required
from werkzeug.wrappers.response import Response

from ..exceptions import exception_handler
from ...reload import reload
from ...sql_migration_list import BrickSQLMigrationList
from ...sql import BrickSQL
from ..upload import upload_helper

logger = logging.getLogger(__name__)

admin_database_page = Blueprint(
    'admin_database',
    __name__,
    url_prefix='/admin/database'
)


# Delete the database
@admin_database_page.route('/delete', methods=['GET'])
@login_required
@exception_handler(__file__)
def delete() -> str:
    return render_template(
        'admin.html',
        delete_database=True,
        database_error=request.args.get('database_error')
    )


# Actually delete the database
@admin_database_page.route('/delete', methods=['POST'])
@login_required
@exception_handler(
    __file__,
    post_redirect='admin_database.delete',
    error_name='database_error'
)
def do_delete() -> Response:
    BrickSQL.delete()

    reload()

    return redirect(url_for('admin.admin'))


# Download the database
@admin_database_page.route('/download', methods=['GET'])
@login_required
@exception_handler(__file__)
def download() -> Response:
    # Create a file name with a timestamp embedded
    name, extension = os.path.splitext(
        os.path.basename(current_app.config['DATABASE_PATH'])
    )

    # Info
    logger.info('The database has been downloaded')

    return send_file(
        current_app.config['DATABASE_PATH'],
        as_attachment=True,
        download_name='{name}-v{version}-{timestamp}{extension}'.format(
            name=name,
            version=BrickSQL(failsafe=True).version,
            timestamp=datetime.now().astimezone(g.timezone).strftime(
                current_app.config['DATABASE_TIMESTAMP_FORMAT']
            ),
            extension=extension
        )
    )


# Drop the database
@admin_database_page.route('/drop', methods=['GET'])
@login_required
@exception_handler(__file__)
def drop() -> str:
    return render_template(
        'admin.html',
        drop_database=True,
        database_error=request.args.get('database_error')
    )


# Actually drop the database
@admin_database_page.route('/drop', methods=['POST'])
@login_required
@exception_handler(
    __file__,
    post_redirect='admin_database.drop',
    error_name='database_error'
)
def do_drop() -> Response:
    BrickSQL.drop()

    reload()

    return redirect(url_for('admin.admin'))


# Actually upgrade the database
@admin_database_page.route('/upgrade', methods=['POST'])
@login_required
@exception_handler(
    __file__,
    post_redirect='admin_database.upgrade',
    error_name='database_error'
)
def do_upgrade() -> Response:
    BrickSQL(failsafe=True).upgrade()

    reload()

    return redirect(url_for('admin.admin'))


# Import a database
@admin_database_page.route('/import', methods=['GET'])
@login_required
@exception_handler(__file__)
def upload() -> str:
    return render_template(
        'admin.html',
        import_database=True,
        database_error=request.args.get('database_error')
    )


# Actually import a database
@admin_database_page.route('/import', methods=['POST'])
@login_required
@exception_handler(
    __file__,
    post_redirect='admin_database.upload',
    error_name='database_error'
)
def do_upload() -> Response:
    file = upload_helper(
        'database',
        'admin_database.upload',
        extensions=['.db'],
    )

    if isinstance(file, Response):
        return file

    BrickSQL.upload(file)

    reload()

    return redirect(url_for('admin.admin'))


# Upgrade the database
@admin_database_page.route('/upgrade', methods=['GET'])
@login_required
@exception_handler(__file__)
def upgrade() -> str | Response:
    database = BrickSQL(failsafe=True)

    if not database.upgrade_needed():
        return redirect(url_for('admin.admin'))

    return render_template(
        'admin.html',
        upgrade_database=True,
        migrations=BrickSQLMigrationList().pending(
            database.version
        ),
        database_error=request.args.get('database_error')
    )
