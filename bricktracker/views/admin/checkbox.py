import logging

from flask import (
    Blueprint,
    jsonify,
    redirect,
    request,
    render_template,
    url_for,
)
from flask_login import login_required
from werkzeug.wrappers.response import Response

from ..exceptions import exception_handler
from ...reload import reload
from ...set_checkbox import BrickSetCheckbox

logger = logging.getLogger(__name__)

admin_checkbox_page = Blueprint(
    'admin_checkbox',
    __name__,
    url_prefix='/admin/checkbox'
)


# Add a checkbox
@admin_checkbox_page.route('/add', methods=['POST'])
@login_required
@exception_handler(
    __file__,
    post_redirect='admin.admin',
    error_name='checkbox_error',
    open_checkbox=True
)
def add() -> Response:
    BrickSetCheckbox().from_form(request.form).insert()

    reload()

    return redirect(url_for('admin.admin', open_checkbox=True))


# Delete the checkbox
@admin_checkbox_page.route('<id>/delete', methods=['GET'])
@login_required
@exception_handler(__file__)
def delete(*, id: str) -> str:
    return render_template(
        'admin.html',
        delete_checkbox=True,
        checkbox=BrickSetCheckbox().select_specific(id),
        error=request.args.get('checkbox_error')
    )


# Actually delete the checkbox
@admin_checkbox_page.route('<id>/delete', methods=['POST'])
@login_required
@exception_handler(
    __file__,
    post_redirect='admin_checkbox.delete',
    error_name='checkbox_error'
)
def do_delete(*, id: str) -> Response:
    checkbox = BrickSetCheckbox().select_specific(id)
    checkbox.delete()

    reload()

    return redirect(url_for('admin.admin', open_checkbox=True))


# Change the status of a checkbox
@admin_checkbox_page.route('/<id>/status/<name>', methods=['POST'])
@login_required
@exception_handler(__file__, json=True)
def update_status(*, id: str, name: str) -> Response:
    value: bool = request.json.get('value', False)  # type: ignore

    checkbox = BrickSetCheckbox().select_specific(id)
    checkbox.update_status(name, value)

    # Info
    logger.info('Checkbox {name} ({id}): status "{status}" changed to "{state}"'.format(  # noqa: E501
        name=checkbox.fields.name,
        id=checkbox.fields.id,
        status=name,
        state=value,
    ))

    reload()

    return jsonify({'value': value})


# Rename the checkbox
@admin_checkbox_page.route('<id>/rename', methods=['POST'])
@login_required
@exception_handler(
    __file__,
    post_redirect='admin.admin',
    error_name='checkbox_error',
    open_checkbox=True
)
def rename(*, id: str) -> Response:
    checkbox = BrickSetCheckbox().select_specific(id)
    checkbox.from_form(request.form).rename()

    reload()

    return redirect(url_for('admin.admin', open_checkbox=True))
