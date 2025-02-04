from flask import Blueprint, redirect, url_for
from flask_login import login_required
from werkzeug.wrappers.response import Response

from ..exceptions import exception_handler
from ...retired_list import BrickRetiredList

admin_retired_page = Blueprint(
    'admin_retired',
    __name__,
    url_prefix='/admin/retired'
)


# Refresh the retired sets cache
@admin_retired_page.route('/refresh', methods=['GET'])
@login_required
@exception_handler(__file__)
def refresh() -> Response:
    BrickRetiredList(force=True)

    return redirect(url_for('admin.admin', open_retired=True))


# Update the retired sets
@admin_retired_page.route('/update', methods=['GET'])
@login_required
@exception_handler(__file__)
def update() -> Response:
    BrickRetiredList().update()

    BrickRetiredList(force=True)

    return redirect(url_for('admin.admin', open_retired=True))
