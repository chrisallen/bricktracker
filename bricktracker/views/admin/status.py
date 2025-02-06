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
from ...set_status import BrickSetStatus

admin_status_page = Blueprint(
    'admin_status',
    __name__,
    url_prefix='/admin/status'
)


# Add a metadata status
@admin_status_page.route('/add', methods=['POST'])
@login_required
@exception_handler(
    __file__,
    post_redirect='admin.admin',
    error_name='status_error',
    open_status=True
)
def add() -> Response:
    BrickSetStatus().from_form(request.form).insert()

    reload()

    return redirect(url_for('admin.admin', open_status=True))


# Delete the metadata status
@admin_status_page.route('<id>/delete', methods=['GET'])
@login_required
@exception_handler(__file__)
def delete(*, id: str) -> str:
    return render_template(
        'admin.html',
        delete_status=True,
        status=BrickSetStatus().select_specific(id),
        status_error=request.args.get('status_error')
    )


# Actually delete the metadata status
@admin_status_page.route('<id>/delete', methods=['POST'])
@login_required
@exception_handler(
    __file__,
    post_redirect='admin_status.delete',
    error_name='status_error'
)
def do_delete(*, id: str) -> Response:
    status = BrickSetStatus().select_specific(id)
    status.delete()

    reload()

    return redirect(url_for('admin.admin', open_status=True))


# Change the field of a metadata status
@admin_status_page.route('/<id>/field/<name>', methods=['POST'])
@login_required
@exception_handler(__file__, json=True)
def update_field(*, id: str, name: str) -> Response:
    status = BrickSetStatus().select_specific(id)
    value = status.update_field(name, json=request.json)

    reload()

    return jsonify({'value': value})


# Rename the metadata status
@admin_status_page.route('<id>/rename', methods=['POST'])
@login_required
@exception_handler(
    __file__,
    post_redirect='admin.admin',
    error_name='status_error',
    open_status=True
)
def rename(*, id: str) -> Response:
    status = BrickSetStatus().select_specific(id)
    status.from_form(request.form).rename()

    reload()

    return redirect(url_for('admin.admin', open_status=True))
