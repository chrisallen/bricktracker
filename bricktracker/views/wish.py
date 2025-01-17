from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required
from werkzeug.wrappers.response import Response

from .exceptions import exception_handler
from ..retired_list import BrickRetiredList
from ..wish import BrickWish
from ..wish_list import BrickWishList

wish_page = Blueprint('wish', __name__, url_prefix='/wishlist')


# Index
@wish_page.route('/', methods=['GET'])
@exception_handler(__file__)
def list() -> str:
    return render_template(
        'wishes.html',
        table_collection=BrickWishList().all(),
        retired=BrickRetiredList(),
        error=request.args.get('error')
    )


# Add a set to the wishlit
@wish_page.route('/add', methods=['POST'])
@login_required
@exception_handler(__file__, post_redirect='wish.list')
def add() -> Response:
    # Grab the set number
    number: str = request.form.get('number', '')

    if number != '':
        BrickWishList.add(number)

    return redirect(url_for('wish.list'))


# Delete a set from the wishlit
@wish_page.route('/delete/<number>', methods=['POST'])
@login_required
@exception_handler(__file__, post_redirect='wish.list')
def delete(*, number: str) -> Response:
    brickwish = BrickWish().select_specific(number)
    brickwish.delete()

    return redirect(url_for('wish.list'))
