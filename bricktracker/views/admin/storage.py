from flask import (
    Blueprint,
    redirect,
    request,
    render_template,
    url_for,
)
from flask_login import login_required
from werkzeug.wrappers.response import Response

from ..exceptions import exception_handler
from ...reload import reload
from ...set_storage import BrickSetStorage

admin_storage_page = Blueprint(
    'admin_storage',
    __name__,
    url_prefix='/admin/storage'
)


# Add a metadata storage
@admin_storage_page.route('/add', methods=['POST'])
@login_required
@exception_handler(
    __file__,
    post_redirect='admin.admin',
    error_name='storage_error',
    open_storage=True
)
def add() -> Response:
    BrickSetStorage().from_form(request.form).insert()

    reload()

    return redirect(url_for('admin.admin', open_storage=True))


# Delete the metadata storage
@admin_storage_page.route('<id>/delete', methods=['GET'])
@login_required
@exception_handler(__file__)
def delete(*, id: str) -> str:
    return render_template(
        'admin.html',
        delete_storage=True,
        storage=BrickSetStorage().select_specific(id),
        error=request.args.get('storage_error')
    )


# Actually delete the metadata storage
@admin_storage_page.route('<id>/delete', methods=['POST'])
@login_required
@exception_handler(
    __file__,
    post_redirect='admin_storage.delete',
    error_name='storage_error'
)
def do_delete(*, id: str) -> Response:
    storage = BrickSetStorage().select_specific(id)
    storage.delete()

    reload()

    return redirect(url_for('admin.admin', open_storage=True))


# Rename the metadata storage
@admin_storage_page.route('<id>/rename', methods=['POST'])
@login_required
@exception_handler(
    __file__,
    post_redirect='admin.admin',
    error_name='storage_error',
    open_storage=True
)
def rename(*, id: str) -> Response:
    storage = BrickSetStorage().select_specific(id)
    storage.from_form(request.form).rename()

    reload()

    return redirect(url_for('admin.admin', open_storage=True))
