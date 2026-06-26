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
from ...set_custom_field import BrickSetCustomField

admin_custom_field_page = Blueprint(
    'admin_custom_field',
    __name__,
    url_prefix='/admin/custom_field'
)


# Add a metadata custom field
@admin_custom_field_page.route('/add', methods=['POST'])
@login_required
@exception_handler(
    __file__,
    post_redirect='admin.admin',
    error_name='custom_field_error',
    open_custom_field=True
)
def add() -> Response:
    BrickSetCustomField().from_form(request.form).insert()

    reload()

    return redirect(url_for('admin.admin', open_custom_field=True))


# Delete the metadata custom field
@admin_custom_field_page.route('<id>/delete', methods=['GET'])
@login_required
@exception_handler(__file__)
def delete(*, id: str) -> str:
    return render_template(
        'admin.html',
        delete_custom_field=True,
        custom_field=BrickSetCustomField().select_specific(id),
        custom_field_error=request.args.get('custom_field_error')
    )


# Actually delete the metadata custom field
@admin_custom_field_page.route('<id>/delete', methods=['POST'])
@login_required
@exception_handler(
    __file__,
    post_redirect='admin_custom_field.delete',
    error_name='custom_field_error'
)
def do_delete(*, id: str) -> Response:
    custom_field = BrickSetCustomField().select_specific(id)
    custom_field.delete()

    reload()

    return redirect(url_for('admin.admin', open_custom_field=True))


# Change a field of a metadata custom field (name or type)
@admin_custom_field_page.route('/<id>/field/<name>', methods=['POST'])
@login_required
@exception_handler(__file__, json=True)
def update_field(*, id: str, name: str) -> Response:
    custom_field = BrickSetCustomField().select_specific(id)
    value = custom_field.update_field(name, json=request.json)

    reload()

    return jsonify({'value': value})


# Rename the metadata custom field
@admin_custom_field_page.route('<id>/rename', methods=['POST'])
@login_required
@exception_handler(
    __file__,
    post_redirect='admin.admin',
    error_name='custom_field_error',
    open_custom_field=True
)
def rename(*, id: str) -> Response:
    custom_field = BrickSetCustomField().select_specific(id)
    custom_field.from_form(request.form).rename()

    reload()

    return redirect(url_for('admin.admin', open_custom_field=True))
