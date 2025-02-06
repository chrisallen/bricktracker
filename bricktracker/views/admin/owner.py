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
from ...set_owner import BrickSetOwner

admin_owner_page = Blueprint(
    'admin_owner',
    __name__,
    url_prefix='/admin/owner'
)


# Add a metadata owner
@admin_owner_page.route('/add', methods=['POST'])
@login_required
@exception_handler(
    __file__,
    post_redirect='admin.admin',
    error_name='owner_error',
    open_owner=True
)
def add() -> Response:
    BrickSetOwner().from_form(request.form).insert()

    reload()

    return redirect(url_for('admin.admin', open_owner=True))


# Delete the metadata owner
@admin_owner_page.route('<id>/delete', methods=['GET'])
@login_required
@exception_handler(__file__)
def delete(*, id: str) -> str:
    return render_template(
        'admin.html',
        delete_owner=True,
        owner=BrickSetOwner().select_specific(id),
        error=request.args.get('owner_error')
    )


# Actually delete the metadata owner
@admin_owner_page.route('<id>/delete', methods=['POST'])
@login_required
@exception_handler(
    __file__,
    post_redirect='admin_owner.delete',
    error_name='owner_error'
)
def do_delete(*, id: str) -> Response:
    owner = BrickSetOwner().select_specific(id)
    owner.delete()

    reload()

    return redirect(url_for('admin.admin', open_owner=True))


# Rename the metadata owner
@admin_owner_page.route('<id>/rename', methods=['POST'])
@login_required
@exception_handler(
    __file__,
    post_redirect='admin.admin',
    error_name='owner_error',
    open_owner=True
)
def rename(*, id: str) -> Response:
    owner = BrickSetOwner().select_specific(id)
    owner.from_form(request.form).rename()

    reload()

    return redirect(url_for('admin.admin', open_owner=True))
