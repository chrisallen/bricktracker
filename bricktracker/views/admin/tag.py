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
from ...set_tag import BrickSetTag

admin_tag_page = Blueprint(
    'admin_tag',
    __name__,
    url_prefix='/admin/tag'
)


# Add a metadata tag
@admin_tag_page.route('/add', methods=['POST'])
@login_required
@exception_handler(
    __file__,
    post_redirect='admin.admin',
    error_name='tag_error',
    open_tag=True
)
def add() -> Response:
    BrickSetTag().from_form(request.form).insert()

    reload()

    return redirect(url_for('admin.admin', open_tag=True))


# Delete the metadata tag
@admin_tag_page.route('<id>/delete', methods=['GET'])
@login_required
@exception_handler(__file__)
def delete(*, id: str) -> str:
    return render_template(
        'admin.html',
        delete_tag=True,
        tag=BrickSetTag().select_specific(id),
        error=request.args.get('tag_error')
    )


# Actually delete the metadata tag
@admin_tag_page.route('<id>/delete', methods=['POST'])
@login_required
@exception_handler(
    __file__,
    post_redirect='admin_tag.delete',
    error_name='tag_error'
)
def do_delete(*, id: str) -> Response:
    tag = BrickSetTag().select_specific(id)
    tag.delete()

    reload()

    return redirect(url_for('admin.admin', open_tag=True))


# Rename the metadata tag
@admin_tag_page.route('<id>/rename', methods=['POST'])
@login_required
@exception_handler(
    __file__,
    post_redirect='admin.admin',
    error_name='tag_error',
    open_tag=True
)
def rename(*, id: str) -> Response:
    tag = BrickSetTag().select_specific(id)
    tag.from_form(request.form).rename()

    reload()

    return redirect(url_for('admin.admin', open_tag=True))
