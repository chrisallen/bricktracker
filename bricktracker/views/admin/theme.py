from flask import Blueprint, redirect, url_for
from flask_login import login_required
from werkzeug.wrappers.response import Response

from ..exceptions import exception_handler
from ...theme_list import BrickThemeList

admin_theme_page = Blueprint(
    'admin_theme',
    __name__,
    url_prefix='/admin/theme'
)


# Refresh the themes cache
@admin_theme_page.route('/refresh', methods=['GET'])
@login_required
@exception_handler(__file__)
def refresh() -> Response:
    BrickThemeList(force=True)

    return redirect(url_for('admin.admin', open_theme=True))


# Update the themes file
@admin_theme_page.route('/update', methods=['GET'])
@login_required
@exception_handler(__file__)
def update() -> Response:
    BrickThemeList().update()

    BrickThemeList(force=True)

    return redirect(url_for('admin.admin', open_theme=True))
