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
from ..minifigure import BrickMinifigure
from ..part import BrickPart
from ..rebrickable_image import RebrickableImage
from ..retired_list import BrickRetiredList
from ..set import BrickSet
from ..sql_counter import BrickCounter
from ..sql_migration_list import BrickSQLMigrationList
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
    database_counters: list[BrickCounter] = []
    database_exception: Exception | None = None
    database_upgrade_needed: bool = False
    database_version: int = -1
    nil_minifigure_name: str = ''
    nil_minifigure_url: str = ''
    nil_part_name: str = ''
    nil_part_url: str = ''

    # This view needs to be protected against SQL errors
    try:
        database = BrickSQL(failsafe=True)
        database_upgrade_needed = database.upgrade_needed()
        database_version = database.version

        if not database_upgrade_needed:
            database_counters = BrickSQL().count_records()
    except Exception as e:
        database_exception = e

        # Warning
        logger.warning('A database exception occured while loading the admin page: {exception}'.format(  # noqa: E501
            exception=str(e),
        ))

    nil_minifigure_name = RebrickableImage.nil_minifigure_name()
    nil_minifigure_url = RebrickableImage.static_url(
        nil_minifigure_name,
        'MINIFIGURES_FOLDER'
    )

    nil_part_name = RebrickableImage.nil_name()
    nil_part_url = RebrickableImage.static_url(
        nil_part_name,
        'PARTS_FOLDER'
    )

    open_image = request.args.get('open_image', None)
    open_instructions = request.args.get('open_instructions', None)
    open_logout = request.args.get('open_logout', None)
    open_retired = request.args.get('open_retired', None)
    open_theme = request.args.get('open_theme', None)

    open_database = (
        open_image is None and
        open_instructions is None and
        open_logout is None and
        open_retired is None and
        open_theme is None
    )

    return render_template(
        'admin.html',
        configuration=BrickConfigurationList.list(),
        database_counters=database_counters,
        database_error=request.args.get('error'),
        database_exception=database_exception,
        database_upgrade_needed=database_upgrade_needed,
        database_version=database_version,
        instructions=BrickInstructionsList(),
        nil_minifigure_name=nil_minifigure_name,
        nil_minifigure_url=nil_minifigure_url,
        nil_part_name=nil_part_name,
        nil_part_url=nil_part_url,
        open_database=open_database,
        open_image=open_image,
        open_instructions=open_instructions,
        open_logout=open_logout,
        open_retired=open_retired,
        open_theme=open_theme,
        retired=BrickRetiredList(),
        theme=BrickThemeList(),
    )


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


# Actually upgrade the database
@admin_page.route('/upgrade-database', methods=['POST'])
@login_required
@exception_handler(__file__, post_redirect='admin.upgrade_database')
def do_upgrade_database() -> Response:
    BrickSQL(failsafe=True).upgrade()

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


# Update the default images
@admin_page.route('/update-image', methods=['GET'])
@login_required
@exception_handler(__file__)
def update_image() -> Response:
    # Abusing the object to create a 'nil' minifigure
    RebrickableImage(
        BrickSet(),
        minifigure=BrickMinifigure(record={
            'set_img_url': None,
        })
    ).download()

    # Abusing the object to create a 'nil' part
    RebrickableImage(
        BrickSet(),
        part=BrickPart(record={
            'part_img_url': None,
            'part_img_url_id': None
        })
    ).download()

    return redirect(url_for('admin.admin', open_image=True))


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


# Upgrade the database
@admin_page.route('/upgrade-database', methods=['GET'])
@login_required
@exception_handler(__file__, post_redirect='admin.admin')
def upgrade_database() -> str | Response:
    database = BrickSQL(failsafe=True)

    if not database.upgrade_needed():
        return redirect(url_for('admin.admin'))

    return render_template(
        'admin.html',
        upgrade_database=True,
        migrations=BrickSQLMigrationList().pending(
            database.version
        ),
        error=request.args.get('error')
    )
