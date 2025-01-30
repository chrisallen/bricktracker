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


# Change the field of a checkbox
@admin_checkbox_page.route('/<id>/field/<name>', methods=['POST'])
@login_required
@exception_handler(__file__, json=True)
def update_field(*, id: str, name: str) -> Response:
    checkbox = BrickSetCheckbox().select_specific(id)
    value = checkbox.update_field(name, json=request.json)

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
