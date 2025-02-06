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
from ...set_purchase_location import BrickSetPurchaseLocation

admin_purchase_location_page = Blueprint(
    'admin_purchase_location',
    __name__,
    url_prefix='/admin/purchase_location'
)


# Add a metadata purchase location
@admin_purchase_location_page.route('/add', methods=['POST'])
@login_required
@exception_handler(
    __file__,
    post_redirect='admin.admin',
    error_name='purchase_location_error',
    open_purchase_location=True
)
def add() -> Response:
    BrickSetPurchaseLocation().from_form(request.form).insert()

    reload()

    return redirect(url_for('admin.admin', open_purchase_location=True))


# Delete the metadata purchase location
@admin_purchase_location_page.route('<id>/delete', methods=['GET'])
@login_required
@exception_handler(__file__)
def delete(*, id: str) -> str:
    return render_template(
        'admin.html',
        delete_purchase_location=True,
        purchase_location=BrickSetPurchaseLocation().select_specific(id),
        error=request.args.get('purchase_location_error')
    )


# Actually delete the metadata purchase location
@admin_purchase_location_page.route('<id>/delete', methods=['POST'])
@login_required
@exception_handler(
    __file__,
    post_redirect='admin_purchase_location.delete',
    error_name='purchase_location_error'
)
def do_delete(*, id: str) -> Response:
    purchase_location = BrickSetPurchaseLocation().select_specific(id)
    purchase_location.delete()

    reload()

    return redirect(url_for('admin.admin', open_purchase_location=True))


# Rename the metadata purchase location
@admin_purchase_location_page.route('<id>/rename', methods=['POST'])
@login_required
@exception_handler(
    __file__,
    post_redirect='admin.admin',
    error_name='purchase_location_error',
    open_purchase_location=True
)
def rename(*, id: str) -> Response:
    purchase_location = BrickSetPurchaseLocation().select_specific(id)
    purchase_location.from_form(request.form).rename()

    reload()

    return redirect(url_for('admin.admin', open_purchase_location=True))
