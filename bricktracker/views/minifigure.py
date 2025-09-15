from flask import Blueprint, render_template, request

from .exceptions import exception_handler
from ..minifigure import BrickMinifigure
from ..minifigure_list import BrickMinifigureList
from ..set_list import BrickSetList, set_metadata_lists
from ..set_owner_list import BrickSetOwnerList

minifigure_page = Blueprint('minifigure', __name__, url_prefix='/minifigures')


# Index
@minifigure_page.route('/', methods=['GET'])
@exception_handler(__file__)
def list() -> str:
    # Get owner filter from request
    owner_id = request.args.get('owner', 'all')

    # Get minifigures filtered by owner
    if owner_id == 'all' or owner_id is None or owner_id == '':
        minifigures = BrickMinifigureList().all()
    else:
        minifigures = BrickMinifigureList().all_by_owner(owner_id)

    # Get list of owners for filter dropdown
    owners = BrickSetOwnerList.list()

    return render_template(
        'minifigures.html',
        table_collection=minifigures,
        owners=owners,
        selected_owner=owner_id,
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
        **set_metadata_lists(as_class=True)
    )
