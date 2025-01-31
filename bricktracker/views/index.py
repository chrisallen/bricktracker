from flask import Blueprint, render_template

from .exceptions import exception_handler
from ..minifigure_list import BrickMinifigureList
from ..set_owner import BrickSetOwner
from ..set_owner_list import BrickSetOwnerList
from ..set_status import BrickSetStatus
from ..set_status_list import BrickSetStatusList
from ..set_tag import BrickSetTag
from ..set_tag_list import BrickSetTagList
from ..set_list import BrickSetList

index_page = Blueprint('index', __name__)


# Index
@index_page.route('/', methods=['GET'])
@exception_handler(__file__)
def index() -> str:
    return render_template(
        'index.html',
        brickset_collection=BrickSetList().last(),
        brickset_owners=BrickSetOwnerList(BrickSetOwner).list(),
        brickset_statuses=BrickSetStatusList(BrickSetStatus).list(),
        brickset_tags=BrickSetTagList(BrickSetTag).list(),
        minifigure_collection=BrickMinifigureList().last(),
    )
