from flask import Blueprint, current_app, render_template
from flask_login import login_required

from ..configuration_list import BrickConfigurationList
from .exceptions import exception_handler
from ..set_owner import BrickSetOwner
from ..set_owner_list import BrickSetOwnerList
from ..set_tag import BrickSetTag
from ..set_tag_list import BrickSetTagList
from ..socket import MESSAGES

add_page = Blueprint('add', __name__, url_prefix='/add')


# Add a set
@add_page.route('/', methods=['GET'])
@login_required
@exception_handler(__file__)
def add() -> str:
    BrickConfigurationList.error_unless_is_set('REBRICKABLE_API_KEY')

    return render_template(
        'add.html',
        brickset_owners=BrickSetOwnerList(BrickSetOwner).list(),
        brickset_tags=BrickSetTagList(BrickSetTag).list(),
        path=current_app.config['SOCKET_PATH'],
        namespace=current_app.config['SOCKET_NAMESPACE'],
        messages=MESSAGES
    )


# Bulk add sets
@add_page.route('/bulk', methods=['GET'])
@login_required
@exception_handler(__file__)
def bulk() -> str:
    BrickConfigurationList.error_unless_is_set('REBRICKABLE_API_KEY')

    return render_template(
        'add.html',
        brickset_owners=BrickSetOwnerList(BrickSetOwner).list(),
        brickset_tags=BrickSetTagList(BrickSetTag).list(),
        path=current_app.config['SOCKET_PATH'],
        namespace=current_app.config['SOCKET_NAMESPACE'],
        messages=MESSAGES,
        bulk=True
    )
