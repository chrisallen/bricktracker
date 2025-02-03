from flask import Blueprint, render_template

from .exceptions import exception_handler
from ..minifigure import BrickMinifigure
from ..minifigure_list import BrickMinifigureList
from ..set_owner_list import BrickSetOwnerList
from ..set_list import BrickSetList
from ..set_storage_list import BrickSetStorageList
from ..set_tag_list import BrickSetTagList

minifigure_page = Blueprint('minifigure', __name__, url_prefix='/minifigures')


# Index
@minifigure_page.route('/', methods=['GET'])
@exception_handler(__file__)
def list() -> str:
    return render_template(
        'minifigures.html',
        table_collection=BrickMinifigureList().all(),
    )


# Minifigure details
@minifigure_page.route('/<figure>/details')
@exception_handler(__file__)
def details(*, figure: str) -> str:
    return render_template(
        'minifigure.html',
        item=BrickMinifigure().select_generic(figure),
        using=BrickSetList().using_minifigure(figure),
        missing=BrickSetList().missing_minifigure(figure),
        damaged=BrickSetList().damaged_minifigure(figure),
        brickset_owners=BrickSetOwnerList.list(),
        brickset_storages=BrickSetStorageList.list(as_class=True),
        brickset_tags=BrickSetTagList.list(),
    )
