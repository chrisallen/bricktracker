from flask import Blueprint, render_template, request
from flask_login import login_required

from ..exceptions import exception_handler
from ...rebrickable_set_list import RebrickableSetList

admin_set_page = Blueprint('admin_set',  __name__, url_prefix='/admin/set')


# Sets that need o be refreshed
@admin_set_page.route('/refresh', methods=['GET'])
@login_required
@exception_handler(__file__)
def refresh() -> str:
    return render_template(
        'admin.html',
        refresh_set=True,
        table_collection=RebrickableSetList().need_refresh(),
        set_error=request.args.get('set_error')
    )
