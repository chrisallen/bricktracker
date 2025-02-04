from flask import Blueprint, redirect, url_for
from flask_login import login_required
from werkzeug.wrappers.response import Response

from ..exceptions import exception_handler
from ...instructions_list import BrickInstructionsList

admin_instructions_page = Blueprint(
    'admin_instructions',
    __name__,
    url_prefix='/admin/instructions'
)


# Refresh the instructions cache
@admin_instructions_page.route('/refresh', methods=['GET'])
@login_required
@exception_handler(__file__)
def refresh() -> Response:
    BrickInstructionsList(force=True)

    return redirect(url_for('admin.admin', open_instructions=True))
