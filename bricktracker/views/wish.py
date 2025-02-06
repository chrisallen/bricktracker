from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    url_for
)
from flask_login import login_required
from werkzeug.wrappers.response import Response

from .exceptions import exception_handler
from ..retired_list import BrickRetiredList
from ..wish import BrickWish
from ..wish_list import BrickWishList
from ..wish_owner_list import BrickWishOwnerList


wish_page = Blueprint('wish', __name__, url_prefix='/wishes')


# Index
@wish_page.route('/', methods=['GET'])
@exception_handler(__file__)
def list() -> str:
    return render_template(
        'wishes.html',
        table_collection=BrickWishList().all(),
        retired=BrickRetiredList(),
        error=request.args.get('error'),
        owners=BrickWishOwnerList.list(),
    )


# Add a set to the wishlit
@wish_page.route('/add', methods=['POST'])
@login_required
@exception_handler(__file__, post_redirect='wish.list')
def add() -> Response:
    # Grab the set
    set: str = request.form.get('set', '')

    if set != '':
        BrickWishList.add(set)

    return redirect(url_for('wish.list'))


# Ask for deletion of a wish
@wish_page.route('/<set>/delete', methods=['GET'])
@login_required
@exception_handler(__file__)
def delete(*, set: str) -> str:
    return render_template(
        'wish.html',
        delete=True,
        item=BrickWish().select_specific(set),
        error=request.args.get('error'),
        owners=BrickWishOwnerList.list(),
    )


# Actually delete of a set
@wish_page.route('/<set>/delete', methods=['POST'])
@login_required
@exception_handler(__file__, post_redirect='wish.list')
def do_delete(*, set: str) -> Response:
    brickwish = BrickWish().select_specific(set)
    brickwish.delete()

    return redirect(url_for('wish.list'))


# Details
@wish_page.route('/<set>/details', methods=['GET'])
@exception_handler(__file__)
def details(*, set: str) -> str:
    return render_template(
        'wish.html',
        item=BrickWish().select_specific(set),
        retired=BrickRetiredList(),
        owners=BrickWishOwnerList.list(),
    )


# Change the state of a owner
@wish_page.route('/<set>/owner/<metadata_id>', methods=['POST'])
@login_required
@exception_handler(__file__, json=True)
def update_owner(*, set: str, metadata_id: str) -> Response:
    brickwish = BrickWish().select_specific(set)
    owner = BrickWishOwnerList.get(metadata_id)

    state = owner.update_wish_state(brickwish, json=request.json)

    return jsonify({'value': state})
