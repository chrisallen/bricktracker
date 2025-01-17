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

from ..configuration_list import BrickConfigurationList
from .exceptions import exception_handler
from ..instructions_list import BrickInstructionsList
from ..retired_list import BrickRetiredList
from ..sql import BrickSQL
from ..theme_list import BrickThemeList
from .upload import upload_helper

logger = logging.getLogger(__name__)

admin_page = Blueprint('admin', __name__, url_prefix='/admin')


# Admin
@admin_page.route('/', methods=['GET'])
@login_required
@exception_handler(__file__)
def admin() -> str:
    counters: dict[str, int] = {}
    exception: Exception | None = None
    is_init: bool = False

    # This view needs to be protected against SQL errors
    try:
        is_init = BrickSQL.is_init()

        if is_init:
            counters = BrickSQL.count_records()
    except Exception as e:
        exception = e

        # Warning
        logger.warning('An exception occured while loading the admin page: {exception}'.format(  # noqa: E501
            exception=str(e),
        ))

    open_instructions = request.args.get('open_instructions', None)
    open_logout = request.args.get('open_logout', None)
    open_retired = request.args.get('open_retired', None)
    open_theme = request.args.get('open_theme', None)

    open_database = (
        open_instructions is None and
        open_logout is None and
        open_retired is None and
        open_theme is None
    )

    return render_template(
        'admin.html',
        configuration=BrickConfigurationList.list(),
        counters=counters,
        error=request.args.get('error'),
        exception=exception,
        instructions=BrickInstructionsList(),
        is_init=is_init,
        open_database=open_database,
        open_instructions=open_instructions,
        open_logout=open_logout,
        open_retired=open_retired,
        open_theme=open_theme,
        retired=BrickRetiredList(),
        theme=BrickThemeList(),
    )


# Initialize the database
@admin_page.route('/init-database', methods=['POST'])
@login_required
@exception_handler(__file__, post_redirect='admin.admin')
def init_database() -> Response:
    BrickSQL.initialize()

    # Reload the instructions
    BrickInstructionsList(force=True)

    return redirect(url_for('admin.admin'))


# Delete the database
@admin_page.route('/delete-database', methods=['GET'])
@login_required
@exception_handler(__file__)
def delete_database() -> str:
    return render_template(
        'admin.html',
        delete_database=True,
        error=request.args.get('error')
    )


# Actually delete the database
@admin_page.route('/delete-database', methods=['POST'])
@login_required
@exception_handler(__file__, post_redirect='admin.delete_database')
def do_delete_database() -> Response:
    BrickSQL.delete()

    # Reload the instructions
    BrickInstructionsList(force=True)

    return redirect(url_for('admin.admin'))


# Download the database
@admin_page.route('/download-database', methods=['GET'])
@login_required
@exception_handler(__file__)
def download_database() -> Response:
    # Create a file name with a timestamp embedded
    name, extension = os.path.splitext(
        os.path.basename(current_app.config['DATABASE_PATH'].value)
    )

    # Info
    logger.info('The database has been downloaded')

    return send_file(
        current_app.config['DATABASE_PATH'].value,
        as_attachment=True,
        download_name='{name}-{timestamp}{extension}'.format(
            name=name,
            timestamp=datetime.now().astimezone(g.timezone).strftime(
                current_app.config['DATABASE_TIMESTAMP_FORMAT'].value
            ),
            extension=extension
        )
    )


# Drop the database
@admin_page.route('/drop-database', methods=['GET'])
@login_required
@exception_handler(__file__)
def drop_database() -> str:
    return render_template(
        'admin.html',
        drop_database=True,
        error=request.args.get('error')
    )


# Actually drop the database
@admin_page.route('/drop-database', methods=['POST'])
@login_required
@exception_handler(__file__, post_redirect='admin.drop_database')
def do_drop_database() -> Response:
    BrickSQL.drop()

    # Reload the instructions
    BrickInstructionsList(force=True)

    return redirect(url_for('admin.admin'))


# Import a database
@admin_page.route('/import-database', methods=['GET'])
@login_required
@exception_handler(__file__)
def import_database() -> str:
    return render_template(
        'admin.html',
        import_database=True,
        error=request.args.get('error')
    )


# Actually import a database
@admin_page.route('/import-database', methods=['POST'])
@login_required
@exception_handler(__file__, post_redirect='admin.import_database')
def do_import_database() -> Response:
    file = upload_helper(
        'database',
        'admin.import_database',
        extensions=['.db'],
    )

    if isinstance(file, Response):
        return file

    BrickSQL.upload(file)

    # Reload the instructions
    BrickInstructionsList(force=True)

    return redirect(url_for('admin.admin'))


# Refresh the instructions cache
@admin_page.route('/refresh-instructions', methods=['GET'])
@login_required
@exception_handler(__file__)
def refresh_instructions() -> Response:
    BrickInstructionsList(force=True)

    return redirect(url_for('admin.admin', open_instructions=True))


# Refresh the retired sets cache
@admin_page.route('/refresh-retired', methods=['GET'])
@login_required
@exception_handler(__file__)
def refresh_retired() -> Response:
    BrickRetiredList(force=True)

    return redirect(url_for('admin.admin', open_retired=True))


# Refresh the themes cache
@admin_page.route('/refresh-themes', methods=['GET'])
@login_required
@exception_handler(__file__)
def refresh_themes() -> Response:
    BrickThemeList(force=True)

    return redirect(url_for('admin.admin', open_theme=True))


# Update the themes file
@admin_page.route('/update-retired', methods=['GET'])
@login_required
@exception_handler(__file__)
def update_retired() -> Response:
    BrickRetiredList().update()

    BrickRetiredList(force=True)

    return redirect(url_for('admin.admin', open_retired=True))


# Update the themes file
@admin_page.route('/update-themes', methods=['GET'])
@login_required
@exception_handler(__file__)
def update_themes() -> Response:
    BrickThemeList().update()

    BrickThemeList(force=True)

    return redirect(url_for('admin.admin', open_theme=True))
